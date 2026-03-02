from flask import Flask, render_template
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
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
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
    
    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    # Register error handlers
    register_error_handlers(app)
    
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

# For local development
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)

# For production (Gunicorn)
import os
app = create_app('production' if os.environ.get('RENDER') else 'development')

# Create tables on first request (not during import)
@app.before_request
def create_tables():
    db.create_all()
    # Remove this function after first call to avoid overhead
    app.before_request_funcs[None].remove(create_tables)
