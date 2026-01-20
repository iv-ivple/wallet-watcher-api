from flask import Flask
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from api.config import config
from api.models import db
from api.routes import wallets_bp, health_bp
from api.workers.scheduler import start_scheduler
from api.utils.errors import register_error_handlers
from api.utils.logging_config import setup_logging

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup logging (do this early)
    setup_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour"]
    )
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(wallets_bp, url_prefix='/api/v1')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Start background scheduler
    if not app.config.get('TESTING', False):
        scheduler = start_scheduler(app)
        
        @app.teardown_appcontext
        def shutdown_scheduler(exception=None):
            # Don't try to shutdown from within a job execution
            if scheduler.running:
                try:
                    scheduler.shutdown(wait=False)
                except RuntimeError:
                    pass  # Ignore if we're in a job thread
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)

# Add this line for production deployment
app = create_app('production')
