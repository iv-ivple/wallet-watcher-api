from web3 import Web3
from cache.redis_client import cache
from config import settings
import requests
import logging
logger = logging.getLogger(__name__)

COINGECKO_API = "https://api.coingecko.com/api/v3"

# Common ERC-20 tokens to check (expand this list)
KNOWN_TOKENS = {
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "DAI":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
}

ERC20_ABI = [
    {"name":"balanceOf","type":"function","inputs":[{"name":"account","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"stateMutability":"view"},
    {"name":"decimals","type":"function","inputs":[],"outputs":[{"name":"","type":"uint8"}],"stateMutability":"view"},
    {"name":"symbol","type":"function","inputs":[],"outputs":[{"name":"","type":"string"}],"stateMutability":"view"},
]

w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))

def get_eth_price_usd() -> float:
    cache_key = "eth_price_usd"
    cached = cache.get(cache_key)
    if cached:
        return cached["price"]
    response = requests.get(f"{COINGECKO_API}/simple/price?ids=ethereum&vs_currencies=usd")
    price = response.json()["ethereum"]["usd"]
    cache.set(cache_key, {"price": price}, ttl=60)  # 1 minute
    return price

def get_token_balance(address: str, token_address: str) -> dict:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI
    )
    raw_balance = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
    decimals = contract.functions.decimals().call()
    symbol = contract.functions.symbol().call()
    human_balance = raw_balance / (10 ** decimals)
    return {"symbol": symbol, "balance": human_balance, "raw": raw_balance}

def get_full_portfolio(address: str) -> dict:
    cache_key = f"portfolio:{address.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    checksum_addr = Web3.to_checksum_address(address)
    eth_balance_wei = w3.eth.get_balance(checksum_addr)
    eth_balance = w3.from_wei(eth_balance_wei, 'ether')
    eth_price = get_eth_price_usd()

    holdings = [{
        "token": "ETH",
        "balance": float(eth_balance),
        "price_usd": eth_price,
        "value_usd": float(eth_balance) * eth_price
    }]

    for symbol, token_addr in KNOWN_TOKENS.items():
        try:
            token_data = get_token_balance(address, token_addr)
            if token_data["balance"] > 0:
                holdings.append({
                    "token": symbol,
                    "balance": token_data["balance"],
                    "price_usd": None,   # Add CoinGecko lookup here
                    "value_usd": None
                })
        except Exception:
            continue

    total_usd = sum(h["value_usd"] for h in holdings if h["value_usd"])

    result = {
        "address": address,
        "total_value_usd": total_usd,
        "holdings": holdings,
        "token_count": len(holdings)
    }
    cache.set(cache_key, result, ttl=300)
    return result
