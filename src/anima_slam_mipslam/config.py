"""Typed config loading for MipSLAM prebuild and evaluation."""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel


class EvalProtocol(BaseModel):
    dataset: str
    root: Path
    scales: list[str]
    expected_native_resolution: tuple[int, int] | None = None


class ComputeConfig(BaseModel):
    backend: str = "auto"
    precision: str = "fp32"
    python_version: str = "3.11"


class DataConfig(BaseModel):
    shared_volume: Path
    repos_volume: Path


class ProjectConfig(BaseModel):
    name: str
    codename: str
    functional_name: str
    wave: int
    paper_arxiv: str


class ModuleConfig(BaseModel):
    project: ProjectConfig
    compute: ComputeConfig
    data: DataConfig


def load_module_config(path: str | Path) -> ModuleConfig:
    with Path(path).open("rb") as handle:
        raw = tomllib.load(handle)
    return ModuleConfig.model_validate(raw)


def load_eval_protocol(path: str | Path) -> EvalProtocol:
    with Path(path).open("rb") as handle:
        raw = tomllib.load(handle)
    return EvalProtocol.model_validate(raw)


def default_eval_root(dataset_name: str) -> Path:
    roots = {
        "replica": Path("/Volumes/AIFlowDev/RobotFlowLabs/datasets/replica"),
        "tum_rgbd": Path("/Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd"),
    }
    try:
        return roots[dataset_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported dataset: {dataset_name}") from exc
