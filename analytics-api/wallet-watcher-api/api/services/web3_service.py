from web3 import Web3
from datetime import datetime
import os
import requests
import time

class Web3Service:
    def __init__(self):
        provider_uri = os.getenv('WEB3_PROVIDER_URI')
        self.w3 = Web3(Web3.HTTPProvider(provider_uri))
        
        # Extract Alchemy API key from provider URI
        # Format: https://eth-mainnet.g.alchemy.com/v2/YOUR-API-KEY
        self.alchemy_url = provider_uri
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to Ethereum node")
    
    def get_balance(self, address):
        """Get ETH balance in Wei, converted to ETH for display"""
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
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
            'value': str(self.w3.from_wei(tx['value'], 'ether')),
            'gas_used': receipt['gasUsed'],
            'gas_price': str(tx['gasPrice']),
            'status': receipt['status']
        }
    
    def get_transactions(self, address, max_count=50):
        """
        Get transaction history for an address using Alchemy's enhanced API
        Uses alchemy_getAssetTransfers which is available on free tier
        """
        try:
            # Use Alchemy's getAssetTransfers method
            # This includes both incoming and outgoing ETH transfers
            
            # Get transactions TO this address (incoming)
            incoming_params = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "alchemy_getAssetTransfers",
                "params": [{
                    "fromBlock": "0x0",
                    "toAddress": address,
                    "category": ["external", "internal"],
                    "maxCount": hex(max_count // 2),  # Split limit between incoming/outgoing
                    "order": "desc"
                }]
            }
            
            # Get transactions FROM this address (outgoing)
            outgoing_params = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "alchemy_getAssetTransfers",
                "params": [{
                    "fromBlock": "0x0",
                    "fromAddress": address,
                    "category": ["external", "internal"],
                    "maxCount": hex(max_count // 2),
                    "order": "desc"
                }]
            }
            
            # Make API calls
            headers = {"Content-Type": "application/json"}
            
            incoming_response = requests.post(
                self.alchemy_url,
                json=incoming_params,
                headers=headers,
                timeout=10
            )
            
            outgoing_response = requests.post(
                self.alchemy_url,
                json=outgoing_params,
                headers=headers,
                timeout=10
            )
            
            transactions = []
            
            # Process incoming transactions
            if incoming_response.status_code == 200:
                incoming_data = incoming_response.json()
                if 'result' in incoming_data:
                    result = incoming_data['result']
                    if result and 'transfers' in result and result['transfers']:
                        for transfer in result['transfers']:
                            transactions.append(self._format_alchemy_transfer(transfer))
            
            # Process outgoing transactions
            if outgoing_response.status_code == 200:
                outgoing_data = outgoing_response.json()
                if 'result' in outgoing_data:
                    result = outgoing_data['result']
                    if result and 'transfers' in result and result['transfers']:
                        for transfer in result['transfers']:
                            transactions.append(self._format_alchemy_transfer(transfer))
            
            # Remove duplicates and sort by block number (descending)
            seen_hashes = set()
            unique_transactions = []
            for tx in transactions:
                if tx['hash'] not in seen_hashes:
                    seen_hashes.add(tx['hash'])
                    unique_transactions.append(tx)
            
            unique_transactions.sort(key=lambda x: x['block_number'], reverse=True)
            
            return unique_transactions[:max_count]
            
        except Exception as e:
            print(f"Error fetching transactions from Alchemy: {e}")
            return []
    
    def _format_alchemy_transfer(self, transfer):
        """Format Alchemy transfer data to our standard format"""
        # Convert block number from hex to int
        block_number = int(transfer['blockNum'], 16)
        
        # Parse timestamp from metadata if available
        timestamp = datetime.now()  # Default to now
        if transfer.get('metadata') and isinstance(transfer['metadata'], dict):
            if 'blockTimestamp' in transfer['metadata']:
                try:
                    timestamp = datetime.fromisoformat(
                        transfer['metadata']['blockTimestamp'].replace('Z', '+00:00')
                    )
                except:
                    pass
        
        # Get value (default to 0 if not present)
        value = transfer.get('value', 0)
        if value == 0:
            value = "0.0"
        else:
            value = str(value)
        
        return {
            'hash': transfer.get('hash', 'unknown'),
            'block_number': block_number,
            'timestamp': timestamp,
            'from_address': transfer.get('from', ''),
            'to_address': transfer.get('to', ''),
            'value': value,
            'gas_used': 0,  # Alchemy doesn't provide this in transfers
            'gas_price': '0',
            'status': 1  # Assume success if it's in the transfer list
        }
    
    def get_latest_block_number(self):
        """Get latest block number"""
        return self.w3.eth.block_number
