FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    JULIA_CPU_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
    JULIA_MODEL_PATH=/models/Julia-1 JULIA_DEVICE=cpu JULIA_MAX_CONCURRENCY=2 \
    JULIA_RATE_LIMIT_RPM=60 JULIA_MAX_BODY_BYTES=262144 JULIA_TRUST_PROXY_HEADERS=true
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
RUN mkdir -p /models && python -c "from huggingface_hub import snapshot_download; snapshot_download('SupersonicLabs/Julia-1', local_dir='/models/Julia-1')" && python -m pip install -e /models/Julia-1
COPY app ./app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 CMD curl -fsS http://127.0.0.1:8000/health || exit 1
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","1","--proxy-headers","--forwarded-allow-ips=*"]
