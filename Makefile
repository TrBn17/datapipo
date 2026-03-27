.PHONY: up down extract install-py extract-py show-config

up:
	docker compose up -d

down:
	docker compose down

extract:
	powershell -ExecutionPolicy Bypass -File scripts/extract_moltbook_sample.ps1

install-py:
	py -3 -m pip install -e .

extract-py:
	py -3 -m lakehouse.cli extract-moltbook

show-config:
	py -3 -m lakehouse.cli show-config
