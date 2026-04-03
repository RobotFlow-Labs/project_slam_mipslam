"""Keyframe and pose-graph backend for online MipSLAM."""

from __future__ import annotations

from dataclasses import dataclass, field

import torch

from anima_slam_mipslam.backend.descriptors import compute_multi_modal_descriptor
from anima_slam_mipslam.backend.sa_pgo import SAPGOResult, SpectralAwarePGO
from anima_slam_mipslam.gaussians.types import (
    FrameBatch,
    GaussianMapState,
    GaussianPrimitive,
    KeyframeRecord,
    PoseGraphEdge,
    PoseGraphState,
)
from anima_slam_mipslam.mapping.filter3d import update_sampling_frequency_from_keyframes


@dataclass
class BackendUpdateResult:
    keyframe_added: bool
    keyframe_id: int | None
    num_keyframes: int
    num_gaussians: int


@dataclass
class MappingBackend:
    active_window_size: int = 4
    keyframe_interval: int = 1
    sa_pgo_interval: int = 2
    optimizer: SpectralAwarePGO = field(default_factory=SpectralAwarePGO)
    keyframes: list[KeyframeRecord] = field(default_factory=list)
    pose_graph: PoseGraphState = field(default_factory=lambda: PoseGraphState(poses=[], edges=[]))

    def update(
        self,
        frame: FrameBatch,
        pose: torch.Tensor,
        map_state: GaussianMapState,
    ) -> BackendUpdateResult:
        frame_index = len(self.pose_graph.poses)
        self.pose_graph.poses.append(pose.clone())
        keyframe_added = frame_index % self.keyframe_interval == 0
        keyframe_id: int | None = None

        if keyframe_added:
            keyframe_id = len(self.keyframes)
            visibility_ids = list(range(len(map_state.gaussians)))
            record = KeyframeRecord(
                keyframe_id=keyframe_id,
                frame=self._clone_frame_with_pose(frame, pose),
                visibility_ids=visibility_ids,
            )
            self.keyframes.append(record)
            self._append_temporal_edge(keyframe_id)
            self._augment_map_from_frame(record.frame, pose, map_state)
            self._refresh_active_window(map_state)
            self._refresh_scale_support(map_state)

        return BackendUpdateResult(
            keyframe_added=keyframe_added,
            keyframe_id=keyframe_id,
            num_keyframes=len(self.keyframes),
            num_gaussians=len(map_state.gaussians),
        )

    def should_run_sa_pgo(self) -> bool:
        if len(self.keyframes) < 2:
            return False
        return len(self.keyframes) % self.sa_pgo_interval == 0

    def run_sa_pgo(self) -> SAPGOResult | None:
        if not self.should_run_sa_pgo():
            return None

        poses = torch.stack(self.pose_graph.poses, dim=0)
        descriptors = torch.stack(
            [
                compute_multi_modal_descriptor(record.frame.rgb, record.frame.depth)
                for record in self.keyframes
            ],
            dim=0,
        )
        result = self.optimizer(poses, descriptors)
        self.pose_graph.poses = [pose.clone() for pose in result.poses]
        self.pose_graph.laplacian_gap = float(result.laplacian_gap)
        return result

    def covisibility_adjacency(self) -> torch.Tensor:
        num_keyframes = len(self.keyframes)
        if num_keyframes == 0:
            return torch.zeros((0, 0), dtype=torch.float32)

        adjacency = torch.zeros((num_keyframes, num_keyframes), dtype=torch.float32)
        for edge in self.pose_graph.edges:
            adjacency[edge.source_id, edge.target_id] = edge.spectral_confidence
            adjacency[edge.target_id, edge.source_id] = edge.spectral_confidence
        return adjacency

    def _append_temporal_edge(self, keyframe_id: int) -> None:
        if keyframe_id == 0:
            return

        source_pose = self.keyframes[keyframe_id - 1].frame.pose
        target_pose = self.keyframes[keyframe_id].frame.pose
        assert source_pose is not None
        assert target_pose is not None
        transform = torch.linalg.inv(source_pose) @ target_pose
        edge = PoseGraphEdge(
            source_id=keyframe_id - 1,
            target_id=keyframe_id,
            transform=transform,
            information=torch.eye(6, dtype=target_pose.dtype, device=target_pose.device),
            spectral_confidence=1.0,
        )
        self.pose_graph.edges.append(edge)

    def _refresh_active_window(self, map_state: GaussianMapState) -> None:
        window = self.keyframes[-self.active_window_size :]
        map_state.active_keyframe_ids = [record.keyframe_id for record in window]

    def _refresh_scale_support(self, map_state: GaussianMapState) -> None:
        if not self.keyframes or not map_state.gaussians:
            return

        active_records = [
            record
            for record in self.keyframes
            if record.keyframe_id in map_state.active_keyframe_ids
        ]
        num_gaussians = len(map_state.gaussians)
        num_keyframes = len(active_records)
        focal_lengths = torch.tensor(
            [
                0.5
                * (
                    float(record.frame.calibration.intrinsics[0, 0])
                    + float(record.frame.calibration.intrinsics[1, 1])
                )
                for record in active_records
            ],
            dtype=torch.float32,
        )
        observed_depths = torch.stack(
            [
                torch.tensor(
                    [float(torch.clamp(gaussian.mean[2], min=1e-3)) for _ in range(num_keyframes)],
                    dtype=torch.float32,
                )
                for gaussian in map_state.gaussians
            ],
            dim=0,
        )
        visibility_mask = torch.ones((num_gaussians, num_keyframes), dtype=torch.bool)
        nu_hat = map_state.global_scale_support
        if nu_hat is None:
            nu_hat = torch.zeros(num_gaussians, dtype=torch.float32)
        elif nu_hat.shape[0] < num_gaussians:
            padding = torch.zeros(num_gaussians - nu_hat.shape[0], dtype=nu_hat.dtype)
            nu_hat = torch.cat([nu_hat, padding], dim=0)
        map_state.global_scale_support = update_sampling_frequency_from_keyframes(
            nu_hat,
            focal_lengths,
            observed_depths,
            visibility_mask,
        )

    @staticmethod
    def _clone_frame_with_pose(frame: FrameBatch, pose: torch.Tensor) -> FrameBatch:
        return FrameBatch(
            rgb=frame.rgb.clone(),
            depth=frame.depth.clone(),
            calibration=frame.calibration,
            pose=pose.clone(),
            timestamp=frame.timestamp,
            source_path=frame.source_path,
            sequence_name=frame.sequence_name,
            scale=frame.scale,
        )

    @staticmethod
    def _augment_map_from_frame(
        frame: FrameBatch,
        pose: torch.Tensor,
        map_state: GaussianMapState,
    ) -> None:
        height, width = frame.depth.shape
        cy = height // 2
        cx = width // 2
        depth = torch.clamp(frame.depth[cy, cx], min=1e-3)
        color = frame.rgb[cy, cx]
        intrinsics = frame.calibration.intrinsics
        fx = intrinsics[0, 0]
        fy = intrinsics[1, 1]
        px = intrinsics[0, 2]
        py = intrinsics[1, 2]
        mean_cam = torch.tensor(
            [
                (cx - px) * depth / fx,
                (cy - py) * depth / fy,
                depth,
            ],
            dtype=frame.depth.dtype,
            device=frame.depth.device,
        )
        mean_world = pose[:3, :3] @ mean_cam + pose[:3, 3]
        primitive = GaussianPrimitive(
            mean=mean_world,
            covariance=torch.eye(3, dtype=frame.depth.dtype, device=frame.depth.device) * 0.01,
            opacity=torch.tensor([0.75], dtype=frame.depth.dtype, device=frame.depth.device),
            sh_coeffs=color.reshape(1, 3),
            color=color,
        )
        map_state.gaussians.append(primitive)
