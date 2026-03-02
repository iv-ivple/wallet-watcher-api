import requests
from cache.redis_client import cache
from config import settings

GRAPH_URL = f"https://gateway.thegraph.com/api/{settings.GRAPH_API_KEY}/subgraphs/id/YOUR_SUBGRAPH_ID"

def get_gas_history(address: str, days: int = 30) -> dict:
    cache_key = f"gas:{address.lower()}:{days}d"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Use The Graph to fetch outgoing transactions
    query = """
    {
      transactions(
        first: 1000,
        where: { from: "%s" },
        orderBy: blockNumber,
        orderDirection: desc
      ) {
        hash
        gasUsed
        gasPrice
        blockNumber
        timestamp
        value
      }
    }
    """ % address.lower()

    response = requests.post(GRAPH_URL, json={"query": query})
    txs = response.json().get("data", {}).get("transactions", [])

    # Aggregate by day
    daily_gas = {}
    total_wei_spent = 0

    for tx in txs:
        gas_cost_wei = int(tx["gasUsed"]) * int(tx["gasPrice"])
        total_wei_spent += gas_cost_wei
        day = tx["timestamp"][:10]  # YYYY-MM-DD
        daily_gas[day] = daily_gas.get(day, 0) + gas_cost_wei

    result = {
        "address": address,
        "period_days": days,
        "total_eth_spent": total_wei_spent / 1e18,
        "transaction_count": len(txs),
        "daily_breakdown": [
            {"date": d, "eth_spent": v / 1e18}
            for d, v in sorted(daily_gas.items())
        ],
        "average_gas_per_tx_eth": (total_wei_spent / len(txs) / 1e18) if txs else 0
    }

    cache.set(cache_key, result, ttl=3600)  # Historical — cache 1 hour
    return result
