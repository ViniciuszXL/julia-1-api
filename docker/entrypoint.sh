#!/bin/sh
set -eu

PROVIDER="${MODEL_PROVIDER:-julia}"

case "$PROVIDER" in
  julia)
    DEFAULT_REPO="SupersonicLabs/Julia-1"
    DEFAULT_DIR="/models/Julia-1"
    MARKER="model.safetensors"
    ;;
  decider)
    DEFAULT_REPO="Mapika/decider-2b"
    DEFAULT_DIR="/models/decider-2b"
    MARKER="decider_config.json"
    ;;
  *)
    echo "[decision-api] Unsupported MODEL_PROVIDER=$PROVIDER (expected julia or decider)." >&2
    exit 1
    ;;
esac

REPO_ID="${MODEL_ID:-$DEFAULT_REPO}"
if [ -n "${MODEL_PATH:-}" ]; then
  MODEL_DIR="$MODEL_PATH"
elif [ "$PROVIDER" = "julia" ] && [ -n "${JULIA_MODEL_PATH:-}" ]; then
  MODEL_DIR="$JULIA_MODEL_PATH"
else
  MODEL_DIR="$DEFAULT_DIR"
fi
MODEL_FILE="$MODEL_DIR/$MARKER"

if [ ! -s "$MODEL_FILE" ]; then
  echo "[decision-api] $PROVIDER model not found in $MODEL_DIR."
  echo "[decision-api] Downloading $REPO_ID to the persistent model volume..."
  mkdir -p "$MODEL_DIR"
  python - "$REPO_ID" "$MODEL_DIR" <<'PY'
import sys
from huggingface_hub import snapshot_download

repo_id, local_dir = sys.argv[1], sys.argv[2]
snapshot_download(repo_id=repo_id, local_dir=local_dir, ignore_patterns=[".git/*"])
PY
  echo "[decision-api] Model download complete."
else
  echo "[decision-api] Reusing cached $PROVIDER model from $MODEL_DIR."
fi

exec "$@"
