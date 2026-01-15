from datetime import datetime
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
        # Get current balance
        current_balance = self.web3_service.get_balance(wallet.address)
        old_balance = int(wallet.balance) if wallet.balance else 0
        
        # Update balance if changed
        if str(current_balance) != wallet.balance:
            logger.info(f"Balance changed for {wallet.address}")
            wallet.balance = str(current_balance)
            
            # Check alerts
            self.check_alerts(wallet, current_balance)
        
        # Update last monitored timestamp
        wallet.last_monitored = datetime.utcnow()
        db.session.commit()
    
    def check_alerts(self, wallet, current_balance):
        """Check if any alerts should trigger"""
        from api.models.alert import Alert
        
        alerts = Alert.query.filter_by(
            wallet_id=wallet.id,
            is_active=True
        ).all()
        
        for alert in alerts:
            threshold = int(alert.threshold)
            
            if alert.alert_type == 'balance_above' and current_balance > threshold:
                self.trigger_alert(alert, wallet, current_balance)
            elif alert.alert_type == 'balance_below' and current_balance < threshold:
                self.trigger_alert(alert, wallet, current_balance)
    
    def trigger_alert(self, alert, wallet, balance):
        """Trigger an alert (log for now, email/webhook later)"""
        logger.warning(
            f"ALERT: {alert.alert_type} triggered for {wallet.address}. "
            f"Balance: {balance} Wei, Threshold: {alert.threshold} Wei"
        )
        alert.last_triggered = datetime.utcnow()
        db.session.commit()
