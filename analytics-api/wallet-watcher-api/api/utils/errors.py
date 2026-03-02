from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API exception"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

class ValidationError(APIError):
    status_code = 400

class NotFoundError(APIError):
    status_code = 404

class RateLimitError(APIError):
    status_code = 429

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        logger.error(f"API Error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Unexpected error occurred")
        return jsonify({'error': 'Internal server error'}), 500
