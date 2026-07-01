import os
from functools import wraps
from flask import Blueprint, request, jsonify
from api.models.api_key import ApiKey, db

auth_bp = Blueprint('auth', __name__)


def require_admin_secret(f):
    """
    Protects API-key-issuing endpoints with a separate admin secret
    (not an ApiKey row) — avoids the chicken-and-egg problem of needing
    a key to create a key.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        provided = request.headers.get('X-Admin-Secret')
        expected = os.environ.get('ADMIN_SECRET')
        if not expected or not provided or provided != expected:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/api-keys', methods=['POST'])
@require_admin_secret
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
