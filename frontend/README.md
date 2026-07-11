# LabCD React Frontend

API-only React client for the LabCD control-system design platform.

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

Ensure the FastAPI backend is running:

```bash
uvicorn backend_api.http.main:app --host 0.0.0.0 --port 8000
```

## Pages

| Route | Pipeline stage |
|-------|----------------|
| `/` | Upload, regularize, pipeline selection |
| `/recommender` | Multi-loop architecture recommendation |
| `/trimmer` | Equilibrium / trim with HITL |
| `/silo` | Single-loop control design |
| `/mulo` | Multi-loop GA optimization |

## Docker

```bash
docker compose up --build
```

Frontend: `http://localhost:5173`  
API: `http://localhost:8000`
