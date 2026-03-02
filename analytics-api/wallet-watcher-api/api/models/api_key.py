import secrets
from datetime import datetime
from api.models import db  # Import db from models/__init__.py

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    
    @staticmethod
    def generate_key():
        """Generate a secure random API key"""
        return secrets.token_urlsafe(48)
    
    def __repr__(self):
        return f'<ApiKey {self.name}>'
