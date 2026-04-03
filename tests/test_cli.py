from pathlib import Path

import torch

from anima_slam_mipslam.cli.run_slam import main


def test_run_sequence_creates_checkpoint(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    exit_code = main(["run-sequence", "--checkpoint", str(checkpoint)])
    assert exit_code == 0
    assert checkpoint.exists()


def test_export_trajectory_writes_text_file(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint.pt"
    output = tmp_path / "trajectory.txt"
    torch.save(
        {"trajectory": torch.stack([torch.eye(4, dtype=torch.float32)], dim=0)},
        checkpoint,
    )
    exit_code = main(
        [
            "export-trajectory",
            "--checkpoint",
            str(checkpoint),
            "--output",
            str(output),
        ]
    )
    assert exit_code == 0
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith("0 ")
