from apscheduler.schedulers.background import BackgroundScheduler
from api.workers.monitor import WalletMonitor
import logging

logger = logging.getLogger(__name__)

def start_scheduler(app):
    """Start background monitoring scheduler"""
    scheduler = BackgroundScheduler()
    monitor = WalletMonitor()
    
    # Schedule monitoring every 60 seconds
    interval = app.config.get('MONITOR_INTERVAL_SECONDS', 60)
    
    scheduler.add_job(
        func=lambda: monitor_with_context(app, monitor),
        trigger='interval',
        seconds=interval,
        id='wallet_monitor',
        name='Monitor all wallets',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler started - monitoring every {interval} seconds")
    
    return scheduler

def monitor_with_context(app, monitor):
    """Run monitor within Flask app context"""
    with app.app_context():
        monitor.monitor_all_wallets()
