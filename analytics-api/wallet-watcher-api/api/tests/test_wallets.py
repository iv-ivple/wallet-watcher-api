import pytest
from api.app import create_app
from api.models.wallet import db, Wallet
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

@patch('api.routes.wallets.Web3.is_address')
@patch('api.routes.wallets.Web3Service')
def test_register_wallet(mock_web3_service_class, mock_is_address, client):
    # Mock Web3.is_address to return True
    mock_is_address.return_value = True
    
    # Create a mock instance
    mock_service_instance = MagicMock()
    mock_service_instance.get_balance.return_value = 1000000000000000000  # 1 ETH
    
    # Make the class constructor return our mock instance
    mock_web3_service_class.return_value = mock_service_instance
    
    # Use the Ethereum address from the test
    response = client.post('/api/v1/wallets', json={
        'address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        'label': 'Test Wallet'
    })
    
    assert response.status_code == 201
    assert response.json['message'] == 'Wallet registered successfully'
    assert 'wallet' in response.json

@patch('api.routes.wallets.Web3Service')
def test_register_invalid_address(mock_web3_service_class, client):
    # Create a mock instance
    mock_service_instance = MagicMock()
    mock_web3_service_class.return_value = mock_service_instance
    
    response = client.post('/api/v1/wallets', json={
        'address': 'invalid-address'
    })
    
    assert response.status_code == 400
    assert 'Invalid Ethereum address' in response.json['error']

