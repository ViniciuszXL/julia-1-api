#!/usr/bin/env python3
import argparse
import concurrent.futures
import http.client
import json
import math
import statistics
import threading
import time
import urllib.parse

PAYLOAD = {
    "state": "A customer reports that the same order was charged twice.",
    "questions": {
        "team": {
            "type": "choice",
            "instructions": "Which team should handle this request?",
            "criteria": {
                "billing": "Billing and payment disputes",
                "shipping": "Shipping and delivery",
                "access": "Account access and login",
            },
        }
    },
}
BODY = json.dumps(PAYLOAD).encode()
_local = threading.local()

def connection(base_url):
    parsed = urllib.parse.urlparse(base_url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    key = (parsed.scheme, parsed.hostname, port)
    cached = getattr(_local, "conn", None)
    if cached and getattr(_local, "key", None) == key:
        return cached, parsed
    cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    conn = cls(parsed.hostname, port, timeout=120)
    _local.conn, _local.key = conn, key
    return conn, parsed

def once(base_url):
    conn, parsed = connection(base_url)
    path = (parsed.path.rstrip("/") if parsed.path else "") + "/v1/decide"
    start = time.perf_counter()
    try:
        conn.request("POST", path, body=BODY, headers={"Content-Type": "application/json", "Connection": "keep-alive"})
        response = conn.getresponse()
        response.read()
    except Exception:
        try:
            conn.close()
        finally:
            _local.conn = None
        raise
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed, response.status

def percentile(values, p):
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)

def main():
    p = argparse.ArgumentParser(description="Benchmark Julia-1 API with persistent HTTP connections.")
    p.add_argument("--url", default="http://127.0.0.1:8000")
    p.add_argument("--requests", type=int, default=40)
    p.add_argument("--concurrency", type=int, default=1)
    p.add_argument("--warmup", type=int, default=3)
    a = p.parse_args()
    if a.requests < 1 or a.concurrency < 1 or a.warmup < 0:
        p.error("requests/concurrency must be >= 1 and warmup >= 0")

    for _ in range(a.warmup):
        once(a.url)

    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.concurrency) as pool:
        results = list(pool.map(lambda _: once(a.url), range(a.requests)))
    elapsed = time.perf_counter() - started

    latencies = [x[0] for x in results]
    statuses = {}
    for _, status in results:
        statuses[str(status)] = statuses.get(str(status), 0) + 1

    success = statuses.get("200", 0)
    output = {
        "requests": a.requests,
        "concurrency": a.concurrency,
        "warmup": a.warmup,
        "success": success,
        "errors": a.requests - success,
        "http_statuses": statuses,
        "elapsed_seconds": round(elapsed, 3),
        "requests_per_second": round(a.requests / elapsed, 3),
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 2),
            "median": round(statistics.median(latencies), 2),
            "p50": round(percentile(latencies, 0.50), 2),
            "p95": round(percentile(latencies, 0.95), 2),
            "p99": round(percentile(latencies, 0.99), 2),
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
        },
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
