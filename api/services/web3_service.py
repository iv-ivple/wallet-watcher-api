from web3 import Web3
from datetime import datetime
import os

class Web3Service:
    def __init__(self):
        provider_uri = os.getenv('WEB3_PROVIDER_URI')
        self.w3 = Web3(Web3.HTTPProvider(provider_uri))
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum node")
    
    def get_balance(self, address):
        """Get ETH balance in Wei"""
        return self.w3.eth.get_balance(address)
    
    def get_transaction_count(self, address):
        """Get number of transactions (nonce)"""
        return self.w3.eth.get_transaction_count(address)
    
    def get_transaction(self, tx_hash):
        """Get transaction details"""
        tx = self.w3.eth.get_transaction(tx_hash)
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        block = self.w3.eth.get_block(tx['blockNumber'])
        
        return {
            'hash': tx_hash,
            'block_number': tx['blockNumber'],
            'timestamp': datetime.fromtimestamp(block['timestamp']),
            'from': tx['from'],
            'to': tx['to'],
            'value': str(tx['value']),
            'gas_used': receipt['gasUsed'],
            'gas_price': str(tx['gasPrice']),
            'status': receipt['status']
        }
    
    def get_latest_block_number(self):
        """Get latest block number"""
        return self.w3.eth.block_number
