# Benchmark

This utility benchmarks a running Julia-1 API instance over HTTP.

## Example

```bash
python benchmark/benchmark.py --url http://127.0.0.1:8000 --requests 100 --concurrency 2
```

It reports total runtime, requests per second, and mean/p50/p95/p99/min/max latency.

For comparable community results, keep the payload unchanged and report CPU model, `JULIA_CPU_THREADS`, `JULIA_MAX_CONCURRENCY`, Docker CPU limit, Python/PyTorch versions, and whether the host was otherwise idle.
