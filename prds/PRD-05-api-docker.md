# PRD-05: API And Docker Packaging

> Module: SLAM-MIPSLAM | Priority: P1
> Depends on: PRD-03, PRD-04
> Status: ⬜ Not started

## Objective
Expose MipSLAM as a service that can build maps, relocalize RGB-D frames, and render alias-free novel views under arbitrary camera settings, packaged in a reproducible Docker image.

## Context (from paper)
The paper’s value proposition is map reuse across changed camera configurations. The service layer must expose that capability directly instead of only shipping an offline research script.

**Paper reference**: Abstract, Sec. I, Sec. IV

## Acceptance Criteria
- [ ] FastAPI service provides health, map-build, render, relocalize, and export endpoints.
- [ ] API accepts camera intrinsics, target resolution, and pose query explicitly.
- [ ] Docker image runs the API and a CLI worker with mounted dataset/model volumes.
- [ ] Service emits render metrics and pose diagnostics per request.
- [ ] Test: `uv run pytest tests/test_api_contract.py tests/test_docker_smoke.py -v` passes.

## Files to Create
| File | Purpose | Paper Ref | Est. Lines |
|------|---------|-----------|-----------|
| `src/anima_slam_mipslam/api/app.py` | FastAPI entrypoint | Abstract, Sec. I | ~180 |
| `src/anima_slam_mipslam/api/schemas.py` | Request/response schemas | Abstract, Sec. I | ~120 |
| `docker/Dockerfile.api` | Container image for service | — | ~80 |
| `docker/docker-compose.api.yml` | Local compose stack | — | ~70 |
| `tests/test_api_contract.py` | Contract tests | — | ~120 |
| `tests/test_docker_smoke.py` | Container startup tests | — | ~100 |

## Architecture Detail (from paper)
### Inputs
- `MapBuildRequest`: dataset path, config, output path
- `RenderRequest`: map checkpoint, pose `Tensor[4,4]`, intrinsics `Tensor[3,3]`, resolution `(H, W)`
- `RelocalizeRequest`: RGB-D frame plus map checkpoint

### Outputs
- `MapBuildResponse`: checkpoint path, summary metrics
- `RenderResponse`: RGB image, depth map, timing stats
- `RelocalizeResponse`: estimated pose, confidence, diagnostics

### Algorithm
```python
@app.post("/v1/map/render")
def render_map(req: RenderRequest) -> RenderResponse:
    map_state = load_map(req.map_path)
    rgb, depth = online_slam.render(map_state, req.camera)
    return RenderResponse(rgb=rgb, depth=depth)
```

## Dependencies
```toml
fastapi = ">=0.115"
uvicorn = ">=0.30"
orjson = ">=3.10"
```

## Data Requirements
| Asset | Size | Path | Download |
|-------|------|------|----------|
| MipSLAM checkpoint | generated artifact | `/Volumes/AIFlowDev/RobotFlowLabs/models/slam/mipslam/` | Built from PRD-03 |

## Test Plan
```bash
uv run pytest tests/test_api_contract.py tests/test_docker_smoke.py -v
```

## References
- Paper: Abstract, Sec. I, Sec. IV
- Depends on: PRD-03, PRD-04
- Feeds into: PRD-07
