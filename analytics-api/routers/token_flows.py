from fastapi import APIRouter
from services.token_flow_service import get_token_flows

router = APIRouter()

@app.get("/token-flows/{address}")
async def token_flows(address: str, days: int = 30):
    return get_token_flows(address, days)
