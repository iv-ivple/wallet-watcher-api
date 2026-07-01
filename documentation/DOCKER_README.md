# Docker Deployment Guide

## Quick Start

### Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

**Note:** the production deployment path has moved to Coolify — see `docker-compose.coolify.yml` in the repo root, which is the current, verified-working compose file. `docker-compose.prod.yml` below has also been fixed (correct env var name, correct Postgres driver prefix, single-worker to avoid duplicate background scheduling) and works if you need a non-Coolify production deploy, but `docker-compose.coolify.yml` is the one actually in use.

```bash
# Build and start (docker-compose.prod.yml — see note above)
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Architecture
```
┌─────────────────┐
│   Flask API     │ :5000
│  (Gunicorn)     │
│  + in-process   │
│    scheduler    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   PostgreSQL    │ :5432
│   (Database)    │
└─────────────────┘
```
Wallet monitoring runs as an in-process background job inside the API container itself (via APScheduler) — there is no separate worker container or service.

## Environment Variables

Required:
- `WEB3_PROVIDER_URI`: Ethereum RPC endpoint (e.g. your Alchemy URL). All three compose files (`docker-compose.yml`, `docker-compose.prod.yml`, `docker-compose.coolify.yml`) now pass this through correctly under this name.
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: PostgreSQL connection string
- `ADMIN_SECRET`: required to create new API keys via `POST /api-keys` (see README_API.md) — present in all three compose files.

## Volumes

- `postgres_data`: Database persistence
- `app_logs`: Application logs (named volume — previously a `./logs` bind mount, which could hit permission issues under Coolify)

## Health Checks

- API: `http://localhost:5000/health` — **note: no `/api/v1` prefix.** The health blueprint is registered without one; only the other API routes live under `/api/v1`.
- Database: `pg_isready` check every 10s

## Troubleshooting

### Container won't start
```bash
docker-compose logs api
docker-compose ps
```
If the API container starts and immediately exits, check that `WEB3_PROVIDER_URI` is actually set and points to a reachable RPC endpoint — the app connects to it eagerly at startup (to start the wallet-monitor scheduler) and will crash immediately if that fails.

### Database connection failed
```bash
docker-compose exec db psql -U walletuser -d walletwatcher
```

### Reset everything
```bash
docker-compose down -v
docker system prune -a
```
