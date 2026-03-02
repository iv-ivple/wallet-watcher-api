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
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Architecture
```
┌─────────────────┐
│   Flask API     │ :5000
│  (Gunicorn)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   PostgreSQL    │ :5432
│   (Database)    │
└─────────────────┘
```

## Environment Variables

Required:
- `RPC_URL`: Ethereum RPC endpoint
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: PostgreSQL connection string

## Volumes

- `postgres_data`: Database persistence
- `./logs`: Application logs

## Health Checks

- API: `http://localhost:5000/api/v1/health`
- Database: `pg_isready` check every 10s

## Troubleshooting

### Container won't start
```bash
docker-compose logs api
docker-compose ps
```

### Database connection failed
```bash
docker-compose exec db psql -U walletuser -d walletwatcher
```

### Reset everything
```bash
docker-compose down -v
docker system prune -a
```
