from web3 import Web3

def validate_address(address: str) -> bool:
    try:
        Web3.to_checksum_address(address)
        return True
    except ValueError:
        return False
