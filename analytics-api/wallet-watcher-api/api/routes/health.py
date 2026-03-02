from flask import Blueprint, jsonify
from sqlalchemy import text
from api.models import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0"
    })
