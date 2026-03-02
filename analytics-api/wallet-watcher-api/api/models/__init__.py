from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models after db is defined to avoid circular imports
from api.models.wallet import Wallet
from api.models.transaction import Transaction
from api.models.alert import Alert
from api.models.api_key import ApiKey

__all__ = ['db', 'Wallet', 'Transaction', 'Alert', 'ApiKey']
