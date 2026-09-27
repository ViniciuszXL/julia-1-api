#!/bin/sh
set -eu

MODEL_DIR="${JULIA_MODEL_PATH:-/models/Julia-1}"
MODEL_FILE="$MODEL_DIR/model.safetensors"
REPO_ID="${JULIA_REPO_ID:-SupersonicLabs/Julia-1}"

if [ ! -s "$MODEL_FILE" ]; then
  echo "[julia-1-api] Julia-1 checkpoint not found in $MODEL_DIR."
  echo "[julia-1-api] Downloading $REPO_ID to the persistent model volume..."
  mkdir -p "$MODEL_DIR"
  python - "$REPO_ID" "$MODEL_DIR" <<'PY'
import sys
from huggingface_hub import snapshot_download

repo_id, local_dir = sys.argv[1], sys.argv[2]
snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    ignore_patterns=[".git/*"],
)
PY
  echo "[julia-1-api] Model download complete."
else
  echo "[julia-1-api] Reusing cached Julia-1 model from $MODEL_DIR."
fi

exec "$@"
