from datetime import datetime
from api.models import db

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(42), unique=True, nullable=False, index=True)
    label = db.Column(db.String(100))
    balance = db.Column(db.String(100), default='0')
    last_monitored = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='wallet', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='wallet', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert wallet to dictionary"""
        return {
            'id': self.id,
            'address': self.address,
            'label': self.label,
            'balance': self.balance,
            'last_monitored': self.last_monitored.isoformat() if self.last_monitored else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Wallet {self.address}>'
