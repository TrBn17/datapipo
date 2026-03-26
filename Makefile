.PHONY: up down extract

up:
	docker compose up -d

down:
	docker compose down

extract:
	powershell -ExecutionPolicy Bypass -File scripts/extract_moltbook_sample.ps1
