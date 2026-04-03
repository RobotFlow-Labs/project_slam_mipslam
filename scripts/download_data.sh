#!/usr/bin/env bash
# Prepare dataset directories and print the paper-aligned download sources.
set -euo pipefail

SHARED="${DATASET_VOLUME:-/Volumes/AIFlowDev/RobotFlowLabs/datasets}"
LOCAL="./data"

echo "=== Downloading datasets for $(basename $(dirname $(dirname $0))) ==="
echo "Shared volume: ${SHARED}"
echo "Local data dir: ${LOCAL}"

mkdir -p "${LOCAL}"
mkdir -p "${SHARED}/replica" "${SHARED}/tum_rgbd"

cat <<'EOF'

Replica dataset
- Paper protocol: 8 evaluation sequences
- Upstream: https://github.com/facebookresearch/Replica-Dataset
- Target path: /Volumes/AIFlowDev/RobotFlowLabs/datasets/replica

TUM RGB-D dataset
- Paper protocol: 3 evaluation sequences
- Upstream: https://cvg.cit.tum.de/data/datasets/rgbd-dataset
- Target path: /Volumes/AIFlowDev/RobotFlowLabs/datasets/tum_rgbd

This script intentionally does not auto-download third-party archives whose
layout differs by source. After placing the datasets in the target folders,
rerun the data preflight and the PRD-04 evaluation pipeline.
EOF
