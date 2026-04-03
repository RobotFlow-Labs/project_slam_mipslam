"""Online RGB-D SLAM orchestration for the MipSLAM scaffold."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import torch

from anima_slam_mipslam.gaussians.types import (
    CameraCalibration,
    FrameBatch,
    GaussianMapState,
    PoseGraphState,
)
from anima_slam_mipslam.mapping.backend import MappingBackend
from anima_slam_mipslam.render.eaa_renderer import EAARenderer
from anima_slam_mipslam.tracking.frontend import TrackingFrontend


@dataclass
class OnlineSLAMResult:
    trajectory: torch.Tensor
    map_state: GaussianMapState
    pose_graph: PoseGraphState
    tracking_losses: list[float]

    def save_checkpoint(self, path: str | Path) -> None:
        payload = {
            "trajectory": self.trajectory,
            "map_state": self.map_state,
            "pose_graph": self.pose_graph,
            "tracking_losses": self.tracking_losses,
        }
        torch.save(payload, Path(path))


class OnlineMipSLAM:
    """Glue tracking, mapping, and SA-PGO into one online loop."""

    def __init__(
        self,
        *,
        frontend: TrackingFrontend | None = None,
        backend: MappingBackend | None = None,
        map_state: GaussianMapState | None = None,
    ) -> None:
        self.frontend = frontend or TrackingFrontend()
        self.backend = backend or MappingBackend()
        self.map_state = map_state or GaussianMapState(gaussians=[])

    def run(self, stream: Iterable[FrameBatch]) -> OnlineSLAMResult:
        trajectory: list[torch.Tensor] = []
        tracking_losses: list[float] = []
        pose_init: torch.Tensor | None = None

        for frame in stream:
            tracking = self.frontend.track(frame, self.map_state, pose_init=pose_init)
            trajectory.append(tracking.pose.clone())
            tracking_losses.append(float(tracking.loss))
            self.backend.update(frame, tracking.pose, self.map_state)

            if self.backend.should_run_sa_pgo():
                result = self.backend.run_sa_pgo()
                if result is not None:
                    trajectory = [pose.clone() for pose in self.backend.pose_graph.poses]

            pose_init = tracking.pose

        if trajectory:
            stacked = torch.stack(trajectory, dim=0)
        else:
            stacked = torch.zeros((0, 4, 4), dtype=torch.float32)

        return OnlineSLAMResult(
            trajectory=stacked,
            map_state=self.map_state,
            pose_graph=self.backend.pose_graph,
            tracking_losses=tracking_losses,
        )

    def render_map(
        self,
        calibration: CameraCalibration,
        *,
        pose_cw: torch.Tensor | None = None,
        renderer: EAARenderer | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        render_impl = renderer or self.frontend.renderer
        return render_impl(self.map_state, calibration, pose_cw=pose_cw)

    @staticmethod
    def export_trajectory(trajectory: torch.Tensor, path: str | Path) -> None:
        output = Path(path)
        rows = trajectory.reshape(trajectory.shape[0], -1).detach().cpu().numpy()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            for index, row in enumerate(rows):
                values = " ".join(f"{value:.6f}" for value in row)
                handle.write(f"{index} {values}\n")
