# Decision: Deployment — Production Server, Workers, Device, HTTPS

## Context
The design document (section 5.2, 10) describes deployment topology and non-functional requirements. This decision captures the production configuration choices.

## Decision
Deploy as a single Uvicorn worker behind a reverse proxy (Nginx/Caddy) with HTTPS. Models loaded once at startup in the worker process.

## Configuration

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Workers** | 1 | FLAN-T5-small + fine-tuned checkpoints share GPU memory; multiple workers would duplicate models |
| **Server** | Uvicorn | FastAPI native, supports lifespan, good performance |
| **Reverse Proxy** | Nginx or Caddy | TLS termination, static file serving, request buffering |
| **HTTPS** | Required | Security, privacy (user text in requests) |
| **Device** | Auto (CUDA if available, else CPU) | Performance; CPU fallback for portability |
| **Model Loading** | Startup (lifespan) | Load once, reuse; fail fast if checkpoints missing |
| **Port** | 8000 (internal) | Reverse proxy maps 443→8000 |
| **Host** | 0.0.0.0 | Accept connections from proxy |

## Model Memory Strategy

- **Both models in memory** (preferred): ~2-3 GB VRAM for FLAN-T5-small × 2
- **If OOM**: Serialize inference (load one, infer, unload, load other) — adds latency
- **Config flag**: `MODEL_LOAD_STRATEGY=both|serialized` (default: `both`)

## Health Endpoint for Load Balancer

`GET /health` returns:
- `status`: "healthy" | "degraded" | "unhealthy"
- `models[].loaded`: boolean per model
- Load balancer should route only to "healthy" or "degraded" (with fallback)

## Environment Variables

```bash
# Required
BASELINE_MODEL_PATH=/app/models/baseline
FINETUNED_MODEL_PATH=/app/models/finetuned

# Optional
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
MODEL_LOAD_STRATEGY=both
CUDA_VISIBLE_DEVICES=0  # If multiple GPUs
```

## Reverse Proxy Config (Nginx Example)

```nginx
server {
    listen 443 ssl http2;
    server_name summarization.example.com;

    ssl_certificate /etc/letsencrypt/live/summarization.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/summarization.example.com/privkey.pem;

    client_max_body_size 1M;

    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;  # Generation can take time
    }
}
```

## Consequences
- Single worker = no horizontal scaling without model sharding
- GPU memory limits max concurrent requests (serialize if needed)
- Reverse proxy handles TLS, static files, buffering
- Health endpoint enables zero-downtime deployments

## Alternatives Considered
- **Multiple workers with shared memory**: Rejected — Transformers models not easily shareable across processes
- **Model server (Triton, vLLM)**: Rejected — overkill for FLAN-T5-small; adds operational complexity
- **CPU-only deployment**: Supported via config; slower but portable

## Status
**Accepted** — Document in `app/config.py` and deployment docs.

## Implementation Notes
- `app/config.py` uses Pydantic Settings with env vars
- `app/main.py` lifespan loads models based on `MODEL_LOAD_STRATEGY`
- Health endpoint checks `model_registry.is_ready(model_id)`
- Reverse proxy config documented in `DEPLOYMENT.md` (create in Phase 6)