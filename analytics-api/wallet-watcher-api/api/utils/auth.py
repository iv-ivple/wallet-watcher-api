from functools import wraps
from flask import request, jsonify
from api.models.api_key import ApiKey, db
from datetime import datetime

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        key = ApiKey.query.filter_by(key=api_key, is_active=True).first()
        
        if not key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Update last used
        key.last_used = datetime.utcnow()
        db.session.commit()
        
        return f(*args, **kwargs)
    
    return decorated_function
