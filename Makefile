.PHONY: dev backend frontend install

install:
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

dev:
	@./start-dev.sh
