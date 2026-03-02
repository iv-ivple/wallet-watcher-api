from fastapi import APIRouter, HTTPException
from utils.validators import validate_address
from services.portfolio_service import get_full_portfolio

router = APIRouter()

@router.get("/analytics/portfolio/{address}")
async def portfolio(address: str):
    if not validate_address(address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    return get_full_portfolio(address)
