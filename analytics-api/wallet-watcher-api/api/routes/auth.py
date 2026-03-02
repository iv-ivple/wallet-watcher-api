from api.utils.auth import require_api_key

@wallets_bp.route('/wallets', methods=['POST'])
@require_api_key
def register_wallet():
    # ... existing code ...

from flask import Blueprint, request, jsonify
from api.models.api_key import ApiKey, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api-keys', methods=['POST'])
def create_api_key():
    """
    Create a new API key
    Body: {"name": "My App"}
    """
    data = request.get_json()
    name = data.get('name', 'Unnamed Key')
    
    api_key = ApiKey(
        key=ApiKey.generate_key(),
        name=name
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    return jsonify({
        'message': 'API key created successfully',
        'api_key': api_key.key,
        'name': api_key.name
    }), 201
