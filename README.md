# Julia-1 API

**English** | [Português (Brasil)](README.pt-BR.md)

A lightweight, Dockerized REST API for [SupersonicLabs/Julia-1](https://huggingface.co/SupersonicLabs/Julia-1), built with FastAPI for CPU-first deployments, Docker, and Coolify.

Julia-1 is a compact decision model designed for classification, routing, scoring, and Boolean decisions rather than generative chat.

## Features

- FastAPI REST interface
- CPU-first deployment
- Docker-ready and Coolify-friendly
- Keeps Julia-1 loaded in memory between requests
- Health check endpoint
- Interactive OpenAPI documentation at `/docs`
- Configuration through environment variables
- Simple `/v1/decide` endpoint

## Quick Start with Docker

```bash
docker build -t julia-1-api .
docker run --rm -p 8000:8000 \
  -e JULIA_CPU_THREADS=4 \
  julia-1-api
```

Open the interactive API documentation at:

```text
http://localhost:8000/docs
```

## API

### Health Check

```bash
curl http://localhost:8000/health
```

### Decision

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

## Deploying with Coolify

Create a new Application in Coolify from this GitHub repository and select **Dockerfile** as the build pack.

Recommended starting configuration:

- Internal port: `8000`
- Health check path: `/health`
- CPU limit: 2-4 CPUs
- Memory limit: 2-4 GB
- Workers: 1
- `JULIA_CPU_THREADS=4`

If the host also runs latency-sensitive workloads, start conservatively and increase the CPU allocation only when benchmarks justify it.

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `JULIA_CPU_THREADS` | `4` | CPU threads available to Julia |
| `JULIA_MODEL_PATH` | `/models/Julia-1` | Model location inside the container |
| `JULIA_DEVICE` | `cpu` | Inference device |

## Repository Structure

```text
.
├── app/
│   └── main.py
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── Dockerfile
├── requirements.txt
├── .env.example
├── .dockerignore
├── .gitignore
├── CONTRIBUTING.md
└── LICENSE
```

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

The `main` branch is intended to receive changes through reviewed pull requests.

## Upstream Project

This repository is an independent API wrapper and is not affiliated with Supersonic Labs.

Julia-1 model artifacts remain subject to the upstream project's license and terms.

## License

The wrapper code in this repository is licensed under the [MIT License](LICENSE).
