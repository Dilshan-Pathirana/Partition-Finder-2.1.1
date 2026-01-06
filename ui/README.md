# PartitionFinder UI (Phase 3 MVP)

React + TypeScript UI that follows the required workflow:

Upload → Configure → Run → Interpret

## Run (development)

Single command (recommended):

```bash
.venv\Scripts\python.exe -m partitionfinder.webapp
```

Manual (two terminals):

1) Start the FastAPI backend (from the repo root):

```bash
.venv\Scripts\python.exe -m uvicorn partitionfinder.api.service:app --reload --port 8000
```

2) Start the UI dev server (from this folder):

```bash
npm install
npm run dev
```

The UI uses a Vite dev proxy for REST calls (`/api/*` → `http://localhost:8000/*`).
For live logs it connects to `ws://localhost:8000/jobs/{id}/stream`.

## Run (production single server)

Builds the UI (if needed) and serves UI + API from a single port:

```bash
.venv\Scripts\python.exe -m partitionfinder.webapp.prod
```

Open:
- http://127.0.0.1:8000

## Screens

- Project Dashboard: lists analyses and statuses
- Data Upload: input folder path + alignment preview
- Configuration Builder: criterion/search/models presets (applied to `.cfg` in the job working folder)
- Live Execution Monitor: progress indicator + live logs + ETA
- Results Explorer: best scheme visualization + scheme score plot + exports
