.PHONY: dev-build
dev-build:
	COMPOSE_BAKE=true docker compose -f provision/docker-compose.yml build

.PHONY: dev-start
dev-start:
	docker compose -f provision/docker-compose.yml up

.PHONY: dev-stop
dev-stop:
	docker compose -f provision/docker-compose.yml down