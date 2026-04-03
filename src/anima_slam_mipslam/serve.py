"""Minimal serving surface for infra verification and later PRD-05 expansion."""

from __future__ import annotations

from fastapi import FastAPI

from .device import get_backend
from .version import __version__

app = FastAPI(title="anima-slam-mipslam", version=__version__)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": __version__, "backend": get_backend()}
