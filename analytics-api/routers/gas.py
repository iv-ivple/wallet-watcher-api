from fastapi import APIRouter, HTTPException, Query
from utils.validators import validate_address
from services.gas_service import get_gas_history

router = APIRouter()

@router.get("/analytics/gas-spent/{address}")
async def gas_spent(address: str, days: int = Query(default=30, ge=1, le=365)):
    if not validate_address(address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    return get_gas_history(address, days)
