from fastapi import APIRouter, Query
from services.portfolio_service import get_full_portfolio
from services.gas_service import get_gas_history
from services.token_flow_service import get_token_flows
import asyncio

router = APIRouter()

@router.get("/analytics/summary/{address}")
async def full_summary(address: str):
    # Run all three services concurrently using asyncio
    portfolio, gas, flows = await asyncio.gather(
        asyncio.to_thread(get_full_portfolio, address),
        asyncio.to_thread(get_gas_history, address, 30),
        asyncio.to_thread(get_token_flows, address, 30)
    )
    return {
        "address": address,
        "portfolio": portfolio,
        "gas_analysis": gas,
        "token_flows": flows
    }

@router.get("/analytics/gas-spent/{address}")
async def gas_spent(
    address: str,
    days: int = Query(default=30, ge=1, le=365),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100)
):
    data = get_gas_history(address, days)
    breakdown = data["daily_breakdown"]
    start = (page - 1) * page_size
    end = start + page_size
    data["daily_breakdown"] = breakdown[start:end]
    data["pagination"] = {
        "page": page,
        "page_size": page_size,
        "total_days": len(breakdown),
        "total_pages": (len(breakdown) + page_size - 1) // page_size
    }
    return data
