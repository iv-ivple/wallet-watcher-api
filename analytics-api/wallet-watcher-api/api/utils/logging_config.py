import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    # Create logs directory
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/wallet_watcher.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info('Wallet Watcher API startup')
