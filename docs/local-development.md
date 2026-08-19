# Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt pytest
cd backend
PYTHONPATH=. pytest -q
```

For the frontend: `cd frontend && cp .env.example .env && npm install && npm run dev`. For the full stack: `docker compose up --build`. Real upgrades remain disabled in compose.
