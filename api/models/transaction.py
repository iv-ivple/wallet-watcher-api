from datetime import datetime
from api.models.wallet import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    tx_hash = db.Column(db.String(66), unique=True, nullable=False, index=True)
    block_number = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.DateTime, index=True)
    from_address = db.Column(db.String(42), index=True)
    to_address = db.Column(db.String(42), index=True)
    value = db.Column(db.String(78))  # Wei as string
    gas_used = db.Column(db.Integer)
    gas_price = db.Column(db.String(78))
    status = db.Column(db.Integer)  # 1 = success, 0 = failed
    
    def to_dict(self):
        return {
        'id': self.id,
        'wallet_id': self.wallet_id,
        'tx_hash': self.tx_hash,
        'from_address': self.from_address,
        'to_address': self.to_address,
        'value': self.value,
        'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        'block_number': self.block_number,
        'status': 'success' if self.status == 1 else 'failed'
        }
