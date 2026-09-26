import asyncio
import os
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException, Request as FastAPIRequest
from pydantic import BaseModel, Field, model_validator
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from julia import load_model

MODEL_PATH = os.getenv("JULIA_MODEL_PATH", "/models/Julia-1")
DEVICE = os.getenv("JULIA_DEVICE", "cpu")
MAX_CONCURRENCY = max(1, int(os.getenv("JULIA_MAX_CONCURRENCY", "2")))
RATE_LIMIT_RPM = max(0, int(os.getenv("JULIA_RATE_LIMIT_RPM", "60")))
MAX_BODY_BYTES = max(1024, int(os.getenv("JULIA_MAX_BODY_BYTES", "262144")))
TRUST_PROXY_HEADERS = os.getenv("JULIA_TRUST_PROXY_HEADERS", "true").lower() in {"1", "true", "yes"}

engine = None
inference_slots = asyncio.Semaphore(MAX_CONCURRENCY)
rate_buckets: dict[str, deque[float]] = defaultdict(deque)
rate_lock = threading.Lock()
metrics_lock = threading.Lock()
metrics = {"requests_total": 0, "inferences_total": 0, "rate_limited_total": 0, "errors_total": 0, "inference_seconds_total": 0.0}


def client_ip(request: FastAPIRequest) -> str:
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def rate_allowed(ip: str) -> bool:
    if RATE_LIMIT_RPM == 0:
        return True
    now = time.monotonic()
    with rate_lock:
        bucket = rate_buckets[ip]
        while bucket and bucket[0] <= now - 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_RPM:
            return False
        bucket.append(now)
        return True


class PublicGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: FastAPIRequest, call_next):
        with metrics_lock:
            metrics["requests_total"] += 1
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > MAX_BODY_BYTES:
                        return JSONResponse({"detail": "Request body too large."}, status_code=413)
                except ValueError:
                    return JSONResponse({"detail": "Invalid Content-Length."}, status_code=400)
            if request.url.path == "/v1/decide" and not rate_allowed(client_ip(request)):
                with metrics_lock:
                    metrics["rate_limited_total"] += 1
                return JSONResponse({"detail": "Rate limit exceeded. Try again later."}, status_code=429, headers={"Retry-After": "60"})
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = load_model(MODEL_PATH, device=DEVICE, strict_encoding=True, max_length=8192, head_length=512)
    yield


app = FastAPI(title="Julia-1 API", description="Community REST API for SupersonicLabs/Julia-1.", version="1.1.0", lifespan=lifespan)
app.add_middleware(PublicGuardMiddleware)


class Question(BaseModel):
    type: Literal["choice", "score", "noul"]
    instructions: str = Field(min_length=1, max_length=4096)
    criteria: dict[str, str] | list[str] | None = None

    @model_validator(mode="after")
    def validate_criteria(self):
        if self.type == "choice" and (not isinstance(self.criteria, dict) or not 2 <= len(self.criteria) <= 20):
            raise ValueError("choice criteria must contain 2 to 20 options.")
        if self.type == "score" and (not isinstance(self.criteria, list) or not 2 <= len(self.criteria) <= 20):
            raise ValueError("score criteria must contain 2 to 20 ordered options.")
        if self.type == "noul" and self.criteria is not None:
            if not isinstance(self.criteria, dict) or set(self.criteria) != {"false", "true"}:
                raise ValueError("noul criteria keys must be exactly 'false' and 'true'.")
        return self


class DecisionRequest(BaseModel):
    state: str = Field(min_length=1, max_length=100_000)
    questions: dict[str, Question] = Field(min_length=1, max_length=64)


@app.get("/")
def root():
    return {"name": "julia-1-api", "model": "SupersonicLabs/Julia-1", "version": app.version, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok" if engine else "starting", "model_loaded": engine is not None, "device": DEVICE}


@app.get("/v1/status")
def status():
    with metrics_lock:
        snapshot = dict(metrics)
    completed = snapshot["inferences_total"]
    snapshot["average_inference_ms"] = round(snapshot["inference_seconds_total"] * 1000 / completed, 2) if completed else 0.0
    return {"model": "SupersonicLabs/Julia-1", "device": DEVICE, "cpu_threads": int(os.getenv("JULIA_CPU_THREADS", "4")), "max_concurrency": MAX_CONCURRENCY, "rate_limit_rpm_per_ip": RATE_LIMIT_RPM, "metrics": snapshot}


@app.post("/v1/decide")
async def decide(payload: DecisionRequest):
    if engine is None:
        raise HTTPException(503, "Model is still loading.")
    questions = {key: value.model_dump(exclude_none=True) for key, value in payload.questions.items()}
    await inference_slots.acquire()
    started = time.perf_counter()
    try:
        result = await run_in_threadpool(lambda: engine.predict(state=payload.state, questions=questions))
        elapsed = time.perf_counter() - started
        with metrics_lock:
            metrics["inferences_total"] += 1
            metrics["inference_seconds_total"] += elapsed
        return result
    except Exception as exc:
        with metrics_lock:
            metrics["errors_total"] += 1
        raise HTTPException(400, str(exc)) from exc
    finally:
        inference_slots.release()
