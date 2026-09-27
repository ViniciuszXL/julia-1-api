FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    JULIA_CPU_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
    JULIA_MODEL_PATH=/models/Julia-1 JULIA_DEVICE=cpu JULIA_MAX_CONCURRENCY=2 \
    JULIA_RATE_LIMIT_RPM=60 JULIA_MAX_BODY_BYTES=262144 JULIA_TRUST_PROXY_HEADERS=true \
    MODEL_PROVIDER=julia
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
# Install Julia-1 source without baking the large model checkpoint into the image.
RUN git clone --depth 1 https://huggingface.co/SupersonicLabs/Julia-1 /opt/julia-1 \
    && rm -rf /opt/julia-1/.git \
    && python -m pip install -e /opt/julia-1
# decider-ai enables MODEL_PROVIDER=decider while Julia remains the default provider.\nCOPY app ./app
COPY docker/entrypoint.sh /usr/local/bin/julia-entrypoint
RUN chmod +x /usr/local/bin/julia-entrypoint && mkdir -p /models
VOLUME ["/models"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 CMD curl -fsS http://127.0.0.1:8000/health || exit 1
ENTRYPOINT ["julia-entrypoint"]
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","1","--proxy-headers","--forwarded-allow-ips=*"]
