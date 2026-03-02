from api.app import create_app
from api.models.api_key import ApiKey
from api.models import db

# Create the Flask app
app = create_app('development')

# Use the app context properly
with app.app_context():
    # Create an API key
    api_key = ApiKey(
        key=ApiKey.generate_key(),
        name="Development Key"
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    print(f"\n{'='*60}")
    print(f"API Key created successfully!")
    print(f"{'='*60}")
    print(f"\nAPI Key: {api_key.key}")
    print(f"Name: {api_key.name}")
    print(f"\n{'='*60}")
    print(f"IMPORTANT: Save this key - you'll need it for API requests!")
    print(f"{'='*60}\n")
