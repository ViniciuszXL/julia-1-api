# Benchmark

This utility benchmarks a running Julia-1 API instance using persistent HTTP/HTTPS connections (keep-alive). It reports throughput, HTTP status counts, and mean/median/p50/p95/p99/min/max client-observed latency.

## Recommended test matrix

Temporarily raise or disable the per-IP rate limit when benchmarking. The default public rate limit can otherwise produce HTTP 429 responses and invalidate the result.

For a local/internal benchmark:

```bash
python benchmark/benchmark.py --url http://127.0.0.1:8000 --requests 40 --concurrency 1
python benchmark/benchmark.py --url http://127.0.0.1:8000 --requests 40 --concurrency 2
python benchmark/benchmark.py --url http://127.0.0.1:8000 --requests 40 --concurrency 4
```

For a public endpoint:

```bash
python benchmark/benchmark.py --url https://julia-1.example.com --requests 40 --concurrency 1
```

The benchmark uses one persistent connection per worker thread, so repeated TLS handshakes do not dominate the measurements.

## Comparing client and server latency

Before a run, note the API's `/v1/status` counters. After the run, query `/v1/status` again. The API's `average_inference_ms` is cumulative since process startup, while this benchmark reports client-observed latency for the current run.

For a clean server-side inference measurement, restart the API before benchmarking or compare the inference counters before and after the run.

For comparable community results, keep the payload unchanged and report CPU model, `JULIA_CPU_THREADS`, `JULIA_MAX_CONCURRENCY`, Docker CPU limit, Python/PyTorch versions, and whether the host was otherwise idle.
