# LabCD React frontend

Primary UI for LabCD (Vite + React + Tailwind).

Full setup, architecture, and development guide: **[../README.md](../README.md)**.

## Dev

```bash
cp .env.example .env
npm install
npm run dev
```

- App: http://localhost:5173  
- Proxies `/api` → `http://localhost:8000`  
- Requires the FastAPI backend running (see root README)

## Scripts

| Command         | Purpose              |
|-----------------|----------------------|
| `npm run dev`   | Vite dev server      |
| `npm run build` | Production build     |
| `npm run lint`  | Oxlint               |
| `npm run preview` | Preview production |

## Structure

| Path | Role |
|------|------|
| `src/api/` | Client, endpoints, types, SSE |
| `src/pages/` | Routes |
| `src/components/` | UI |
| `src/context/` | Auth / theme / pipeline session |
| `src/hooks/` | Job stream / poll helpers |
| `src/lib/` | Parsers and display helpers |

Do not put control-design or LLM business logic here — call the API instead.
