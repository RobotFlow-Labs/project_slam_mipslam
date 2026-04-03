from pathlib import Path

from anima_slam_mipslam.config import load_eval_protocol, load_module_config


def test_module_config_parses() -> None:
    config = load_module_config(Path("configs/default.toml"))
    assert config.project.name == "anima-slam-mipslam"
    assert config.compute.python_version == "3.11"


def test_eval_protocol_parses() -> None:
    protocol = load_eval_protocol(Path("configs/eval/replica.toml"))
    assert protocol.dataset == "replica"
    assert protocol.scales == ["2x", "1x", "1/2", "1/4", "1/8"]
