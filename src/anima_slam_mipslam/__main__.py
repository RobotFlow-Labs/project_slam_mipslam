"""Package entrypoint for smoke tests and CLI usage."""

from __future__ import annotations

import sys

from .cli.run_slam import main as cli_main
from .device import get_backend
from .version import __version__


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        return cli_main(args)
    print(f"anima_slam_mipslam {__version__} backend={get_backend()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
