# Julia-1 API

Dockerized REST API for [SupersonicLabs/Julia-1](https://huggingface.co/SupersonicLabs/Julia-1), built with FastAPI for CPU-first deployments, Docker, and Coolify.

Julia-1 is a compact decision model for classification, routing, scoring, and Boolean decisions rather than generative chat.

## Features

- FastAPI REST interface
- CPU-first Docker image
- Model stays loaded between requests
- Health check endpoint
- Interactive OpenAPI docs at `/docs`
- Ready for Coolify

## Docker

```bash
docker build -t julia-1-api .
docker run --rm -p 8000:8000 -e JULIA_CPU_THREADS=4 julia-1-api
```

Then visit `http://localhost:8000/docs`.

## API

```bash
curl http://localhost:8000/health
```

Example decision:

```bash
curl -X POST http://localhost:8000/v1/decide \
  -H "Content-Type: application/json" \
  -d '{
    "state": "A customer reports a duplicate charge.",
    "questions": {
      "team": {
        "type": "choice",
        "instructions": "Which team should handle this?",
        "criteria": {
          "billing": "Billing and payment disputes",
          "shipping": "Shipping and delivery",
          "access": "Account access"
        }
      }
    }
  }'
```

## Coolify

Create an Application from this repository and select the **Dockerfile** build pack.

Recommended starting point:

- Internal port: `8000`
- Health check: `/health`
- CPU limit: 2-4 CPUs
- Memory limit: 2-4 GB
- `JULIA_CPU_THREADS=4`

For hosts running other latency-sensitive workloads, start conservatively and increase CPU only when benchmarks justify it.

## Environment

| Variable | Default | Purpose |
| --- | --- | --- |
| `JULIA_CPU_THREADS` | `4` | CPU threads used by Julia |
| `JULIA_MODEL_PATH` | `/models/Julia-1` | Model location |
| `JULIA_DEVICE` | `cpu` | Inference device |

## Upstream

This repository is an independent wrapper and is not affiliated with Supersonic Labs. Julia-1 model artifacts remain subject to the upstream license and terms.

## License

Wrapper code is licensed under MIT.
