from pathlib import Path

import cv2
import numpy as np
import torch

from anima_slam_mipslam.data.replica import ReplicaSequence
from anima_slam_mipslam.data.tum_rgbd import TUMRGBDSequence


def _write_rgb(path: Path, shape: tuple[int, int, int]) -> None:
    image = np.full(shape, 127, dtype=np.uint8)
    cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


def _write_depth(path: Path, shape: tuple[int, int]) -> None:
    depth = np.full(shape, 1000, dtype=np.uint16)
    cv2.imwrite(str(path), depth)


def test_replica_scale_protocol(tmp_path: Path) -> None:
    (tmp_path / "rgb").mkdir()
    (tmp_path / "depth").mkdir()
    _write_rgb(tmp_path / "rgb" / "000000.png", (6, 8, 3))
    _write_depth(tmp_path / "depth" / "000000.png", (6, 8))
    pose = " ".join(str(v) for v in np.eye(4, dtype=np.float32).reshape(-1))
    (tmp_path / "traj.txt").write_text(pose)

    sequence = ReplicaSequence(tmp_path, scale="1/2")
    sample = sequence[0]
    assert sample.rgb.shape[:2] == (3, 4)
    assert sample.depth.shape == (3, 4)
    assert sample.calibration.intrinsics.shape == (3, 3)
    assert sample.pose is not None


def test_tum_sequence_reads_associations(tmp_path: Path) -> None:
    (tmp_path / "rgb").mkdir()
    (tmp_path / "depth").mkdir()
    _write_rgb(tmp_path / "rgb" / "000000.png", (4, 6, 3))
    _write_depth(tmp_path / "depth" / "000000.png", (4, 6))
    (tmp_path / "association.txt").write_text("0.0 rgb/000000.png 0.0 depth/000000.png\n")

    sequence = TUMRGBDSequence(tmp_path, scale="2x")
    sample = sequence[0]
    assert sample.rgb.shape[:2] == (8, 12)
    assert torch.is_tensor(sample.depth)
    assert sample.timestamp == 0.0
