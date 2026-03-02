import requests
from cache.redis_client import cache
from config import settings
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def get_token_flows(address: str, days: int = 30) -> dict:
    cache_key = f"flows:{address.lower()}:{days}d"
    cached = cache.get(cache_key)
    if cached:
        return cached

    checksum = Web3.to_checksum_address(address)
    blocks_back = days * 7200  # ~7200 blocks/day on Ethereum
    current_block = w3.eth.block_number
    from_block = max(0, current_block - blocks_back)

    # Get incoming transfers (address is the `to` topic)
    address_padded = "0x" + checksum[2:].zfill(64)

    inbound_logs = w3.eth.get_logs({
        "fromBlock": from_block,
        "toBlock": "latest",
        "topics": [TRANSFER_TOPIC, None, address_padded]
    })

    outbound_logs = w3.eth.get_logs({
        "fromBlock": from_block,
        "toBlock": "latest",
        "topics": [TRANSFER_TOPIC, address_padded, None]
    })

    def process_logs(logs, direction):
        flows = {}
        for log in logs:
            token = log["address"]
            value = int(log["data"], 16)
            if token not in flows:
                flows[token] = {"token_address": token, "direction": direction, "total_raw": 0, "tx_count": 0}
            flows[token]["total_raw"] += value
            flows[token]["tx_count"] += 1
        return list(flows.values())

    inflows = process_logs(inbound_logs, "inbound")
    outflows = process_logs(outbound_logs, "outbound")

    result = {
        "address": address,
        "period_days": days,
        "inbound_tx_count": len(inbound_logs),
        "outbound_tx_count": len(outbound_logs),
        "net_tx_count": len(inbound_logs) - len(outbound_logs),
        "inflows": inflows,
        "outflows": outflows
    }

    cache.set(cache_key, result, ttl=1800)
    return result
