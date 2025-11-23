.PHONY: dev backend frontend install

install:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

backend:
	source backend/venv/bin/activate && uvicorn backend.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@echo "Starting Backend and Frontend..."
	@trap 'kill 0' EXIT; \
	source backend/venv/bin/activate && uvicorn backend.main:app --reload --port 8000 & \
	cd frontend && npm run dev
