from datetime import datetime
from api.models.wallet import db

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    alert_type = db.Column(db.String(20))  # 'balance_above', 'balance_below', 'transaction'
    threshold = db.Column(db.String(78))  # For balance alerts (in Wei)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
        'id': self.id,
        'wallet_id': self.wallet_id,
        'alert_type': self.alert_type,
        'threshold': self.threshold,
        'is_active': self.is_active,
        'created_at': self.created_at.isoformat() if self.created_at else None
    }
