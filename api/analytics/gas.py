from flask import Blueprint, jsonify, request
from web3 import Web3
import os
from api.cache.redis_client import cache

gas_bp = Blueprint('gas', __name__)
RPC_URL = os.getenv("RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def validate_address(address):
    try:
        Web3.to_checksum_address(address)
        return True
    except ValueError:
        return False

@gas_bp.route('/analytics/gas-spent/<address>', methods=['GET'])
def get_gas_spent(address):
    if not validate_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400

    days = request.args.get('days', 30, type=int)
    days = max(1, min(days, 365))

    cache_key = f"gas:{address.lower()}:{days}d"
    cached = cache.get(cache_key)
    if cached:
        cached["cached"] = True
        return jsonify(cached)

    try:
        checksum = Web3.to_checksum_address(address)
        blocks_back = days * 7200
        current_block = w3.eth.block_number
        from_block = max(0, current_block - blocks_back)

        # Get all transactions sent by this address via eth_getLogs is not ideal for tx history
        # We'll use a block scan approach with nonce to estimate count
        nonce = w3.eth.get_transaction_count(checksum)
        
        result = {
            "address": address,
            "period_days": days,
            "total_transactions_sent": nonce,
            "note": "Full gas history requires The Graph API. Add GRAPH_API_KEY to .env for detailed breakdown.",
            "current_block": current_block,
            "from_block": from_block,
            "cached": False
        }
        cache.set(cache_key, result, ttl=3600)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
