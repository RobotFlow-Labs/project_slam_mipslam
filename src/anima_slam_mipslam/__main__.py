"""Module entrypoint for quick environment smoke tests."""

from .device import get_backend
from .version import __version__


def main() -> None:
    print(f"anima_slam_mipslam {__version__} backend={get_backend()}")


if __name__ == "__main__":
    main()

