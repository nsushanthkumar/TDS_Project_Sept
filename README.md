# LLM App Generator API

## Overview
This service exposes a single HTTP endpoint that takes a brief and optional checks/attachments, generates a single‑page HTML app using an LLM, creates or updates a GitHub repository with that app, enables GitHub Pages for hosting, updates the README, notifies an external evaluation API, and logs evidence of the transaction. The public route remains stable as `POST /api-endpoint` and there is a `GET /health` for readiness checks.

Core flow:
- Validate and parse request
- Optional: fetch prior `index.html` for iterative rounds
- Generate `index.html` via LLM (Gemini-compatible OpenAI API, fallback supported)
- Upload large embedded assets as repository files under `assets/` and rewrite references
- Create or update the GitHub repo and enable GitHub Pages
- Generate and update `README.md`
- Notify external evaluation API and log evidence asynchronously

## Architecture
The codebase is modular with clear boundaries between HTTP, orchestration, providers, and infrastructure.

- `app/__init__.py` — App factory; sets up logging, validates env, registers routes
- `app/api/routes.py` — Flask blueprint exposing `POST /api-endpoint` and `GET /health`
- `app/api/schemas.py` — Pydantic request/response models
- `app/domain/models.py` — Core typed models (request, repo info, notification)
- `app/domain/use_cases.py` — `GenerateAndPublishApp` orchestrates the full flow
- `app/services/` — Service layer with thin adapters
  - `llm_service.py` — LLM generation for app code and README
  - `repo_service.py` — Repo operations facade
  - `notifier.py` — Evaluation API notifier with retries
  - `evidence_logger.py` — Async evidence logging
  - `providers/llm_openai.py` — OpenAI SDK (Gemini-compatible) implementation
  - `providers/utils_attachments.py` — Compact attachment summarization
  - `vcs/github_manager.py` — GitHub repo + Pages management
  - `vcs/html_assets.py` — Data‑URI extraction → upload to `assets/` → rewrite HTML
- `app/infra/` — Cross‑cutting concerns
  - `settings.py` — Pydantic Settings (`.env`) and validation
  - `logging.py` — JSON structured logging setup
- Entrypoints
  - `api/index.py` — Vercel entry that imports `create_app()`
  - `main.py` — Local runner that builds the app and starts Flask

Request and response contracts are enforced at the HTTP boundary via Pydantic models, while providers (LLM, VCS, notifier) are cleanly separated for testability and swaps.

## Setup
Prerequisites:
- Python 3.12+
- A GitHub Personal Access Token with repo permissions
- An OpenAI‑compatible API key (Gemini via OpenAI SDK), optionally a fallback key

Environment variables (place in `.env` in the project root):
- `GITHUB_TOKEN` — GitHub PAT
- `GITHUB_USERNAME` — Your GitHub username
- `OPENAI_API_KEY` — Primary key for Gemini (OpenAI‑compatible endpoint)
- `SECRET` — Shared secret for request validation
- `PORT` — Optional, defaults to 5000
- `AIPIPE_AKI_KEY` — Optional fallback LLM key

Install dependencies:
- Using pip and `requirements.txt`:
  - `pip install -r requirements.txt`
- Or using uv (if you prefer pyproject workflow):
  - `uv run python -V` (ensures env)
  - `uv run python main.py`

## How to run
Local development:
- Start the server: `python main.py`
- Health check: `GET http://localhost:5000/health`
- Main endpoint: `POST http://localhost:5000/api-endpoint`

Expected request JSON (fields):
- Required: `email`, `secret`, `round` (int >= 1), `nonce`, `brief`, `evaluation_url`
- Optional: `task` (repo name), `checks` (list of strings), `attachments` (list)

Response JSON (success):
- `status`: `"success"`
- `repo_url`: GitHub repository URL
- `pages_url`: GitHub Pages URL
- `commit_sha`: latest commit sha
- `warning`: optional if evaluator notification failed after retries

Deployment (Vercel):
- `vercel.json` rewrites to `api/index`, which exposes the Flask app via `create_app()`
- Configure the same environment variables in your Vercel project

Notes:
- Large inline assets found in the generated HTML are extracted and uploaded under `assets/` in the target repo, and references are rewritten.
- GitHub Pages provisioning can take time to become live after first enablement.
