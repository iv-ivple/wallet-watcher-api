from api.app import create_app
from api.models import db

# Import all models to ensure they're registered
from api.models.wallet import Wallet
from api.models.transaction import Transaction
from api.models.alert import Alert
from api.models.api_key import ApiKey

# Create the Flask app
app = create_app('development')

# Use the app context
with app.app_context():
    # Create all tables
    db.create_all()
    print("Database initialized successfully!")
    print(f"Tables created: {db.metadata.tables.keys()}")
