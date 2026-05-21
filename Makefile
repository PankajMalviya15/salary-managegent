# ──────────────────────────────────────────────
# Salary Management Tool — Developer Makefile
# ──────────────────────────────────────────────
# Usage:
#   make setup          — first-time setup (venv + npm install)
#   make seed           — seed database with 10,000 employees
#   make dev-backend    — start FastAPI dev server
#   make dev-frontend   — start Next.js dev server
#   make test-backend   — run backend tests
#   make test-frontend  — run frontend tests
# ──────────────────────────────────────────────

.PHONY: setup setup-backend setup-frontend seed dev-backend dev-frontend test-backend test-frontend clean

# ── Paths ──────────────────────────────────────
BACKEND_DIR   := backend
FRONTEND_DIR  := frontend
VENV          := $(BACKEND_DIR)/.venv
PIP           := $(VENV)/bin/pip
PYTHON        := $(VENV)/bin/python
UVICORN       := $(VENV)/bin/uvicorn
PYTEST        := $(VENV)/bin/pytest
ALEMBIC       := $(VENV)/bin/alembic

# ── Setup ──────────────────────────────────────

setup: setup-backend setup-frontend
	@echo ""
	@echo "✅  Setup complete! Next steps:"
	@echo "    1. cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env"
	@echo "    2. cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env.local"
	@echo "    3. make seed"
	@echo "    4. make dev-backend  (terminal 1)"
	@echo "    5. make dev-frontend (terminal 2)"

setup-backend:
	@echo "🐍  Setting up backend..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "✅  Backend dependencies installed."

setup-frontend:
	@echo "⚛️   Setting up frontend..."
	cd $(FRONTEND_DIR) && npm install
	@echo "✅  Frontend dependencies installed."

# ── Seed ───────────────────────────────────────

seed:
	@echo "🌱  Seeding database..."
	cd $(BACKEND_DIR) && $(PYTHON) -m seed.seed
	@echo "✅  Database seeded."

seed-small:
	@echo "🌱  Seeding database (100 rows)..."
	cd $(BACKEND_DIR) && $(PYTHON) -m seed.seed --count 100
	@echo "✅  Database seeded with 100 rows."

# ── Dev Servers ────────────────────────────────

dev-backend:
	@echo "🚀  Starting FastAPI dev server on http://localhost:8000 ..."
	cd $(BACKEND_DIR) && $(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "🚀  Starting Next.js dev server on http://localhost:3000 ..."
	cd $(FRONTEND_DIR) && npm run dev

# ── Migrations ─────────────────────────────────

migrate:
	@echo "📦  Running database migrations..."
	cd $(BACKEND_DIR) && $(ALEMBIC) upgrade head

migration:
	@echo "📦  Generating migration..."
	cd $(BACKEND_DIR) && $(ALEMBIC) revision --autogenerate -m "$(msg)"

# ── Tests ──────────────────────────────────────

test-backend:
	@echo "🧪  Running backend tests..."
	cd $(BACKEND_DIR) && $(PYTEST) -v --cov=app --cov-report=term-missing

test-frontend:
	@echo "🧪  Running frontend tests..."
	cd $(FRONTEND_DIR) && npm test

# ── Cleanup ────────────────────────────────────

clean:
	@echo "🧹  Cleaning up..."
	rm -rf $(VENV)
	rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/.next
	rm -f $(BACKEND_DIR)/*.db
	@echo "✅  Clean complete."
