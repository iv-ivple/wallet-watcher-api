import time
import logging
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import portfolio, gas, summary
from cache.redis_client import cache
from config import settings

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

ADMIN_SECRET = settings.ADMIN_SECRET

app = FastAPI(title="Web3 Analytics API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Timing middleware
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        return response

app.add_middleware(TimingMiddleware)

app.include_router(portfolio.router)
app.include_router(gas.router)
app.include_router(summary.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

@app.delete("/cache/{address}")
def invalidate_cache(address: str, x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    patterns = [f"portfolio:{address.lower()}*", f"gas:{address.lower()}*", f"flows:{address.lower()}*"]
    for p in patterns:
        cache.delete_pattern(p)
    return {"message": f"Cache cleared for {address}"}

@app.get("/cache/stats")
def cache_stats():
    return {"hit_rate_percent": round(cache.hit_rate, 2), "hits": cache._hits, "misses": cache._misses}
