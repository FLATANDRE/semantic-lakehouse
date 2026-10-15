.PHONY: up pipeline test down openmetadata-up metadata lineage
up:
	docker compose up -d --build
pipeline:
	./scripts/run_pipeline.sh
test:
	python -m pytest -q
openmetadata-up:
	docker compose -f docker-compose.openmetadata.yml up -d
metadata:
	docker compose --profile governance run --rm -e OPENMETADATA_JWT_TOKEN openmetadata-runner metadata ingest -c config/trino.yaml
lineage:
	docker compose --profile governance run --rm -e OPENMETADATA_JWT_TOKEN openmetadata-runner metadata ingest -c config/openlineage.yaml
down:
	docker compose down -v
