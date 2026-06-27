build-rag:
	docker compose -f deployment/docker-compose.yml up --build

down-rag:
	docker compose -f deployment/docker-compose.yml down