from datetime import datetime, timezone
import logging
from api.models import db
from api.models.wallet import Wallet
from api.models.transaction import Transaction
from api.services.web3_service import Web3Service

logger = logging.getLogger(__name__)

class WalletMonitor:
    def __init__(self):
        self.web3_service = Web3Service()
    
    def monitor_all_wallets(self):
        """Check all registered wallets for updates"""
        logger.info("Starting wallet monitoring cycle")
        
        wallets = Wallet.query.all()
        
        for wallet in wallets:
            try:
                self.check_wallet(wallet)
            except Exception as e:
                logger.error(f"Error monitoring wallet {wallet.address}: {e}")
        
        logger.info(f"Completed monitoring {len(wallets)} wallets")
    
    def check_wallet(self, wallet):
        """Check a single wallet for new transactions"""
        # Get current balance (now returns float in ETH)
        current_balance = self.web3_service.get_balance(wallet.address)
        old_balance = float(wallet.balance) if wallet.balance else 0.0
        
        # Update balance if changed
        if current_balance != old_balance:
            logger.info(f"Balance changed for {wallet.address}: {old_balance} ETH -> {current_balance} ETH")
            wallet.balance = str(current_balance)
            
            # Check alerts
            self.check_alerts(wallet, current_balance)
        
        # Fetch and store recent transactions
        self.sync_transactions(wallet)
        
        # Update last monitored timestamp
        wallet.last_monitored = datetime.now(timezone.utc)
        db.session.commit()
    
    def sync_transactions(self, wallet):
        """Sync transaction history for a wallet"""
        try:
            # Fetch transactions from blockchain
            transactions = self.web3_service.get_transactions(wallet.address)
            
            if not transactions:
                logger.info(f"No transactions found for {wallet.address}")
                return
            
            # Store new transactions
            for tx_data in transactions:
                # Check if transaction already exists
                existing = Transaction.query.filter_by(
                    tx_hash=tx_data['hash']  # Use tx_hash to match your model
                ).first()
                
                if existing:
                    continue  # Skip if already stored
                
                # Create new transaction record
                transaction = Transaction(
                    wallet_id=wallet.id,
                    tx_hash=tx_data['hash'],  # Use tx_hash field name
                    block_number=tx_data['block_number'],
                    timestamp=tx_data['timestamp'],
                    from_address=tx_data['from_address'],
                    to_address=tx_data['to_address'],
                    value=tx_data['value'],
                    gas_used=tx_data['gas_used'],
                    gas_price=tx_data['gas_price'],
                    status=tx_data['status']
                )
                
                db.session.add(transaction)
            
            db.session.commit()
            logger.info(f"Synced transactions for {wallet.address}")
            
        except Exception as e:
            logger.error(f"Error syncing transactions for {wallet.address}: {e}")
            db.session.rollback()
    
    def check_alerts(self, wallet, current_balance):
        """Check if any alerts should trigger"""
        from api.models.alert import Alert
        
        alerts = Alert.query.filter_by(
            wallet_id=wallet.id,
            is_active=True
        ).all()
        
        for alert in alerts:
            try:
                threshold = float(alert.threshold) if alert.threshold else 0.0
                
                if alert.alert_type == 'balance_above' and current_balance > threshold:
                    self.trigger_alert(alert, wallet, current_balance)
                elif alert.alert_type == 'balance_below' and current_balance < threshold:
                    self.trigger_alert(alert, wallet, current_balance)
                elif alert.alert_type == 'balance_change':
                    # Trigger on any balance change
                    self.trigger_alert(alert, wallet, current_balance)
            except Exception as e:
                logger.error(f"Error checking alert {alert.id}: {e}")
    
    def trigger_alert(self, alert, wallet, balance):
        """Trigger an alert (log for now, email/webhook later)"""
        logger.warning(
            f"ALERT: {alert.alert_type} triggered for {wallet.address}. "
            f"Balance: {balance} ETH, Threshold: {alert.threshold} ETH"
        )
        alert.last_triggered = datetime.now(timezone.utc)
        db.session.commit()
