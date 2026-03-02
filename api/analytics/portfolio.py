from flask import Blueprint, jsonify, request
from web3 import Web3
import requests
import os
from api.cache.redis_client import cache

portfolio_bp = Blueprint('portfolio', __name__)

RPC_URL = os.getenv("RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

KNOWN_TOKENS = {
    "USDC": ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
    "USDT": ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
    "DAI":  ("0x6B175474E89094C44Da98b954EedeAC495271d0F", 18),
    "WETH": ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
}

ERC20_ABI = [
    {"name":"balanceOf","type":"function","inputs":[{"name":"account","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"stateMutability":"view"},
    {"name":"decimals","type":"function","inputs":[],"outputs":[{"name":"","type":"uint8"}],"stateMutability":"view"},
]

def validate_address(address: str) -> bool:
    try:
        Web3.to_checksum_address(address)
        return True
    except ValueError:
        return False

@portfolio_bp.route('/analytics/portfolio/<address>', methods=['GET'])
def get_portfolio(address):
    if not validate_address(address):
        return jsonify({"error": "Invalid Ethereum address"}), 400

    cache_key = f"portfolio:{address.lower()}"
    cached = cache.get(cache_key)
    if cached:
        cached["cached"] = True
        return jsonify(cached)

    try:
        checksum = Web3.to_checksum_address(address)
        eth_wei = w3.eth.get_balance(checksum)
        eth_balance = float(w3.from_wei(eth_wei, 'ether'))

        # Get ETH price
        eth_price = 0
        try:
            price_resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                timeout=5
            )
            eth_price = price_resp.json()["ethereum"]["usd"]
        except Exception:
            pass

        holdings = [{
            "token": "ETH",
            "balance": eth_balance,
            "price_usd": eth_price,
            "value_usd": eth_balance * eth_price
        }]

        for symbol, (token_addr, decimals) in KNOWN_TOKENS.items():
            try:
                contract = w3.eth.contract(
                    address=Web3.to_checksum_address(token_addr),
                    abi=ERC20_ABI
                )
                raw = contract.functions.balanceOf(checksum).call()
                balance = raw / (10 ** decimals)
                if balance > 0.001:
                    holdings.append({
                        "token": symbol,
                        "balance": balance,
                        "price_usd": None,
                        "value_usd": None
                    })
            except Exception:
                continue

        total_usd = sum(h["value_usd"] for h in holdings if h["value_usd"])
        result = {
            "address": address,
            "total_value_usd": total_usd,
            "holdings": holdings,
            "token_count": len(holdings),
            "cached": False
        }
        cache.set(cache_key, result, ttl=300)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
