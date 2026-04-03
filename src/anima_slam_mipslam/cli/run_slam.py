"""Small CLI entrypoints for the online MipSLAM scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from anima_slam_mipslam.pipeline.online_slam import OnlineMipSLAM


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="anima-slam-mipslam")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_sequence = subparsers.add_parser("run-sequence")
    run_sequence.add_argument("--checkpoint", required=True)

    render_map = subparsers.add_parser("render-map")
    render_map.add_argument("--checkpoint", required=True)
    render_map.add_argument("--output", required=True)

    export_traj = subparsers.add_parser("export-trajectory")
    export_traj.add_argument("--checkpoint", required=True)
    export_traj.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    checkpoint_path = Path(args.checkpoint)

    if args.command == "run-sequence":
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"status": "placeholder"}, checkpoint_path)
        return 0

    payload = torch.load(checkpoint_path, map_location="cpu")

    if args.command == "render-map":
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        rgb = payload.get("rendered_rgb")
        if rgb is None:
            raise ValueError("Checkpoint does not contain rendered_rgb")
        torch.save(rgb, output)
        return 0

    if args.command == "export-trajectory":
        trajectory = payload.get("trajectory")
        if trajectory is None:
            raise ValueError("Checkpoint does not contain trajectory")
        OnlineMipSLAM.export_trajectory(trajectory, args.output)
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2
