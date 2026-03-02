from flask import Blueprint, jsonify, request
from web3 import Web3
import os
from api.cache.redis_client import cache

flows_bp = Blueprint('token_flows', __name__)
RPC_URL = os.getenv("RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def validate_address(address):
    try:
        Web3.to_checksum_address(address)
        return True
    except ValueError:
        return False

@flows_bp.route('/analytics/token-flows/<address>', methods=['GET'])
def get_token_flows(address):
    if not validate_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400

    days = request.args.get('days', 7, type=int)
    days = max(1, min(days, 30))  # Keep small — RPC log queries are expensive

    cache_key = f"flows:{address.lower()}:{days}d"
    cached = cache.get(cache_key)
    if cached:
        cached["cached"] = True
        return jsonify(cached)

    try:
        checksum = Web3.to_checksum_address(address)
        blocks_back = days * 7200
        current_block = w3.eth.block_number
        from_block = current_block - blocks_back
        address_padded = "0x" + checksum[2:].lower().zfill(64)

        inbound = w3.eth.get_logs({
            "fromBlock": hex(from_block),
            "toBlock": "latest",
            "topics": [TRANSFER_TOPIC, None, address_padded]
        })

        outbound = w3.eth.get_logs({
            "fromBlock": hex(from_block),
            "toBlock": "latest",
            "topics": [TRANSFER_TOPIC, address_padded, None]
        })

        def aggregate(logs):
            flows = {}
            for log in logs:
                token = log["address"]
                value = int(log["data"].hex() if hasattr(log["data"], "hex") else log["data"], 16)
                if token not in flows:
                    flows[token] = {"token_address": token, "transfer_count": 0, "total_raw": 0}
                flows[token]["transfer_count"] += 1
                flows[token]["total_raw"] += value
            return list(flows.values())

        result = {
            "address": address,
            "period_days": days,
            "inbound_count": len(inbound),
            "outbound_count": len(outbound),
            "inflows": aggregate(inbound),
            "outflows": aggregate(outbound),
            "cached": False
        }
        cache.set(cache_key, result, ttl=1800)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
