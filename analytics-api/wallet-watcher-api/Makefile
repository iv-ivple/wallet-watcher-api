.PHONY: build up down logs shell db-shell test clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec api bash

db-shell:
	docker-compose exec db psql -U walletuser -d walletwatcher

test:
	docker-compose exec api pytest

clean:
	docker-compose down -v
	docker system prune -f
