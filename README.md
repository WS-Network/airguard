# AirGuard

**Multimodal AI for networking analysis & safe automation.**
Monorepo with a Next.js web UI, an Express/Prisma API gateway, and a FastAPI **ai-core** service (model parsing, explanations, diagrams, and change planning). Designed to run on your Windows 11 + WSL2 dev box today and drop onto the **NVIDIA Jetson Orin Nano Developer Kit (JetPack 6.2)** later with no API changes.

---

## Table of contents

* [Architecture](#architecture)
* [Repo layout](#repo-layout)
* [Tech stack](#tech-stack)
* [Prerequisites](#prerequisites)
* [Quickstart (Docker Compose)](#quickstart-docker-compose)
* [Local dev (hot reload)](#local-dev-hot-reload)
* [Environment variables](#environment-variables)
* [API contracts (ai-core)](#api-contracts-ai-core)
* [Datasets pipeline (programmatic)](#datasets-pipeline-programmatic)
* [Testing](#testing)
* [Observability](#observability)
* [Security model](#security-model)
* [Jetson Orin Nano notes](#jetson-orin-nano-notes)
* [Troubleshooting](#troubleshooting)
* [Decisions (pros/cons) & picks](#decisions-proscons--picks)
* [Roadmap](#roadmap)
* [License](#license)

---

## Architecture

```
Next.js (web)  ──▶  Express/Prisma (api, gateway)  ──▶  FastAPI (ai-core)
        ▲                        │                         ▲
        └──────────── http ◀────┴─────── mTLS/JWT ────────┘
                                     Postgres (db)

Datasets/  →  tools(datasets/normalize/topo2diagram)  →  trainsets/* (JSONL)
```

**Key idea:** keep AI in a separate service so we can swap runtimes (PyTorch now, TensorRT-LLM on Jetson later) without touching the web/API.

---

## Repo layout

```
apps/
  web/           # Next.js + Tailwind UI
  api/           # Express + Prisma + proxy to ai-core
services/
  ai-core/       # FastAPI + model tooling + dataset CLI
    tools/
      datasets/  # Typer CLI (fetch/convert/build)
      normalize/ # parsers (e.g., FRR → OpenConfig-ish JSON)
      topo2diagram/ # GraphML → draw.io/Mermaid converters
datasets/
  topologies/ traffic/ telemetry/ configs/ diagrams/ licenses/ trainsets/
docker/
  docker-compose.yml
package.json     # root scripts for datasets and dev helpers
```

---

## Tech stack

* **Web:** Next.js (TypeScript), Tailwind CSS
* **API:** Express.js, Prisma, PostgreSQL
* **AI:** FastAPI (Python 3.11), Pydantic, (TensorRT-LLM on Jetson later)
* **Data tooling:** Typer, pandas, networkx, jsonschema
* **Runtime:** Docker & Docker Compose (multi-service)

---

## Prerequisites

* **Windows 11 + WSL2 (Ubuntu)**
* **Docker Desktop** (WSL2 backend enabled; Ubuntu integration on)
* **VS Code** + extensions: *WSL*, *Docker*, *ESLint*, *Prettier*, *Python*, *Pylance*
* **Node.js 20** (via `nvm`) + **pnpm**
* (Datasets) **awscli** for CIC-IDS2018 sync

> If you haven’t set up WSL2/Docker yet, ask and I’ll paste the exact commands.

---

## Quickstart (Docker Compose)

> All commands in this README assume **WSL Ubuntu terminal** and the repo root: `~/dev/airguard`

1. Build and start core services:

```bash
cd docker
docker compose build ai-core api web
docker compose up -d postgres
# wait until postgres is healthy:
docker compose up -d ai-core api web
```

2. Sanity checks:

```bash
# ai-core health
curl -H "Authorization: Bearer dev-token" http://localhost:8088/healthz
# api health
curl http://localhost:3001/healthz
# web
# open http://localhost:3000/parse and click "Parse"
```

**What this does**

* `api` auto-runs Prisma migrations on start.
* `web` can call `/ai/parse-config` through the API gateway.

---

## Local dev (hot reload)

Run services locally (faster iteration), or mix with Compose:

```bash
# Terminal 1 (ai-core)
cd services/ai-core
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AI_DEV_JWT=dev-token
uvicorn main:app --host 0.0.0.0 --port 8088 --reload

# Terminal 2 (api)
cd apps/api
pnpm install
pnpm dev

# Terminal 3 (web)
cd apps/web
pnpm install
pnpm dev
```

---

## Environment variables

**apps/api/.env** (Compose injects these; for local dev set them yourself)

```
PORT=3001
AI_CORE_URL=http://localhost:8088
AI_DEV_JWT=dev-token
DATABASE_URL=postgresql://airguard:airguard@localhost:5432/airguard
```

**apps/web/.env.local**

```
NEXT_PUBLIC_API_URL=http://localhost:3001
```

**services/ai-core/.env** (optional for local)

```
AI_DEV_JWT=dev-token
```

---

## API contracts (ai-core)

ai-core exposes 5 endpoints (Express proxies `/ai/*` to these):

* `POST /parse-config` → `{ normalized, confidence, warnings }`
* `POST /explain-setup` → `{ markdown, highlights[] }`
* `POST /generate-diagram` → `{ format, data }` (draw\.io JSON or Mermaid)
* `POST /plan-changes` → `{ diff[], dryRun{}, blastRadius[] }`
* `POST /validate` → `{ ok, errors[], metrics{} }`

Get the OpenAPI spec:

```bash
curl http://localhost:8088/openapi.json -o services/ai-core/openapi.json
```

Generate a TS declaration:

```bash
pnpm add -D openapi-typescript
pnpm dlx openapi-typescript services/ai-core/openapi.json -o packages/shared/src/ai.d.ts
```

---

## Datasets pipeline (programmatic)

> Outputs land under `datasets/…` and a `datasets/catalog.csv` tracks provenance & licenses.

**Install venv & init catalog**

```bash
pnpm run ds:venv
pnpm run ds:init
```

**Pull schemas & telemetry**

```bash
pnpm run ds:openconfig
pnpm run ds:cisco-telemetry
```

**CIC-IDS2018 (labeled flows)**

```bash
sudo apt -y install awscli
pnpm run ds:cic      # sync + normalize to JSONL
```

**Topology Zoo (download the ZIP once to your Windows Downloads)**

```bash
# edit the path if different
pnpm run ds:topozoo
pnpm run ds:convert-graphs  # GraphML → internal JSON + Mermaid + draw.io JSON
```

**Build parser trainset (pairs of raw config + normalized JSON)**

```bash
pnpm run ds:parser-trainset
```

**Check artifacts**

```bash
column -s, -t < datasets/catalog.csv | less
ls datasets/diagrams | head
head -n 1 datasets/trainsets/parser_v1/train.jsonl | jq .
```

> The dataset CLI lives in `services/ai-core/tools/datasets/cli.py`. Converters are in `tools/topo2diagram/` and `tools/normalize/`.

---

## Testing

**API (Jest)**

```bash
cd apps/api
pnpm test
```

Supertest hits `GET /healthz` and `POST /ai/parse-config`.

**ai-core (pytest)**

```bash
cd services/ai-core
source .venv/bin/activate
pytest -q
```

---

## Observability

* **API:** `pino-http` logs request metadata (method, path, status, ms).
* **ai-core:** a simple timing middleware prints latency per endpoint.

Inspect logs:

```bash
docker logs -f $(docker ps --filter name=api --format "{{.ID}}")
docker logs -f $(docker ps --filter name=ai-core --format "{{.ID}}")
```

---

## Security model

* **Dev:** short-lived **JWT** from API → ai-core (env `AI_DEV_JWT`).
* **Prod (Jetson / on-prem):** **mTLS** between API ↔ ai-core (recommended), SNMPv3 authPriv, SSH keys (ed25519), HTTPS (TLS 1.3).
* **At rest (Jetson):** LUKS-encrypted data partition; secrets in encrypted store.

---

## Jetson Orin Nano notes

* Target **JetPack 6.2.x (Jetson Linux 36.4.x)**; deploy the **same containers**.
* Enable **“Super Mode”** for extra performance when benchmarking on device.
* Convert the tiny models to **TensorRT-LLM** (INT8/INT4) for on-device inference.
* Use a supported Wi-Fi NIC (M.2-E/USB) if you need AP mode for dongle pairing.

> We can wire a multi-arch build (`linux/amd64`, `linux/arm64`) once you’re ready to ship to Orin Nano.

---

## Troubleshooting

**ai-core fails to build**

* Ensure `services/ai-core/requirements.txt` exists and the Dockerfile matches this README.
* Rebuild:

  ```bash
  cd docker && docker compose build ai-core && docker compose up -d ai-core
  docker logs -f $(docker ps --filter name=ai-core --format "{{.ID}}")
  ```

**API can’t reach Postgres**

* Check health: `docker compose ps`
* Shell into DB:

  ```bash
  docker exec -it $(docker ps --filter name=postgres --format "{{.ID}}") \
    psql -U airguard -d airguard -c "\dt"
  ```

**Prisma migration not applied**

* API Dockerfile must run `pnpm run start:prod` (which runs `prisma migrate deploy`).
* Inspect API logs for migration output.

**CIC-IDS2018 sync fails**

* Install `awscli` in WSL; rerun `pnpm run ds:cic`.
* Disk space: check `df -h`.

---

## Decisions (pros/cons) & picks

**Separate ai-core service (FastAPI) vs merge into Node**

* * Clear boundary, easy Jetson runtime swap, independent scaling
* – Another container to operate
* **Pick:** Separate **ai-core** (future-proof).

**JSONL vs Parquet for trainsets**

* * Streamable, LLM-friendly, easy diffs
* – Larger on disk
* **Pick:** **JSONL** now; Parquet later for analytics.

**draw\.io vs Mermaid for diagrams**

* * ops-grade editor & schema
* – Heavier JSON
* **Pick:** **draw\.io** primary; generate Mermaid for docs.

**Dev auth: JWT vs mTLS**

* * JWT simple for dev & CI
* – Weaker than mTLS
* **Pick:** **JWT in dev**, **mTLS in prod**.

**Compose vs direct local**

* * Matches production/Jetson; fewer “works on my machine” issues
* – Slightly slower iteration
* **Pick:** **Compose** for team runs; local hot-reload for coding.

---

## Roadmap

* **Graph role inference** (centrality → core/dist/access) in `topo2diagram/convert.py`.
* **Gate-0 vendor parsers** (TextFSM/TTP for Cisco/MikroTik) + expand trainsets.
* **Parser SFT** (tiny model) + constrained JSON decoding & validators.
* **Diagram validator tests** (hierarchy, link types, VLAN tags).
* **TensorRT-LLM engines** for Jetson Orin Nano + perf bakeoff.
* **mTLS** between API ↔ ai-core; encrypted secrets store on Jetson.

---

## License

TBD. Until then, treat the repo as “all-rights-reserved” internally.
Each dataset’s license/ToU is tracked in `datasets/licenses/` and `datasets/catalog.csv`.

---

### Maintainers

* WS-Network — AirGuard core
* Ping me to generate an **OpenAPI TS SDK**, **CI pipeline**, or a **multi-arch Docker build** file next.