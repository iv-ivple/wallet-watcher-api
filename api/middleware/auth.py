from functools import wraps
from flask import request, jsonify
from api.models import db
from api.models.api_key import ApiKey
from datetime import datetime

def require_api_key(f):
    """
    Decorator to require API key authentication for endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        key_obj = ApiKey.query.filter_by(key=api_key, is_active=True).first()
        
        if not key_obj:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Update last used timestamp
        key_obj.last_used_at = datetime.utcnow()
        db.session.commit()
        
        # Call the actual endpoint
        return f(*args, **kwargs)
    
    return decorated_function
