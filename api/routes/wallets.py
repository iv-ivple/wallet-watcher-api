from flask import Blueprint, request, jsonify
from web3 import Web3
from api.models import db
from api.models.wallet import Wallet
from api.models.transaction import Transaction
from api.models.alert import Alert
from api.middleware.auth import require_api_key
from api.services.web3_service import Web3Service  # ADD THIS LINE
from datetime import datetime

wallets_bp = Blueprint('wallets', __name__)

def get_web3_service():
    """Lazy initialization of Web3Service - only creates instance when first called"""
    if not hasattr(get_web3_service, '_instance'):
        get_web3_service._instance = Web3Service()
    return get_web3_service._instance

@wallets_bp.route('/wallets', methods=['POST'])
def register_wallet():
    """Register a new wallet for monitoring"""
    data = request.get_json()
    
    if not data or 'address' not in data:
        return jsonify({'error': 'Address is required'}), 400
    
    address = data['address']
    label = data.get('label', '')
    
    # Validate Ethereum address format
    if not Web3.is_address(address):
        return jsonify({'error': 'Invalid Ethereum address'}), 400
    
    # Convert to checksum address (proper format)
    address = Web3.to_checksum_address(address)

    # Check if wallet already exists
    existing_wallet = Wallet.query.filter_by(address=address).first()
    if existing_wallet:
        return jsonify({'error': 'Wallet already registered'}), 409
    
    # Get balance from blockchain
    web3_service = get_web3_service()
    balance = web3_service.get_balance(address)
    
    # Create new wallet
    wallet = Wallet(
    address=address,
    label=data.get('label'),
    balance=str(balance)  # Convert to string
)
    
    db.session.add(wallet)
    db.session.commit()
    
    return jsonify({
        'message': 'Wallet registered successfully',
        'wallet': wallet.to_dict()
    }), 201

@wallets_bp.route('/wallets/<address>', methods=['GET'])
def get_wallet(address):
    """Get wallet information"""
    if not Web3.is_address(address):
        return jsonify({'error': 'Invalid Ethereum address'}), 400
    
    wallet = Wallet.query.filter_by(address=address).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    return jsonify({'wallet': wallet.to_dict()}), 200

@wallets_bp.route('/wallets', methods=['GET'])
def list_wallets():
    """List all registered wallets"""
    wallets = Wallet.query.all()
    return jsonify({
        'wallets': [wallet.to_dict() for wallet in wallets],
        'count': len(wallets)
    }), 200

@wallets_bp.route('/wallets/<address>/transactions', methods=['GET'])
def get_wallet_transactions(address):
    """Get transactions for a wallet"""
    if not Web3.is_address(address):
        return jsonify({'error': 'Invalid Ethereum address'}), 400
    
    wallet = Wallet.query.filter_by(address=address).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    transactions = Transaction.query.filter_by(wallet_id=wallet.id).order_by(Transaction.timestamp.desc()).all()
    
    return jsonify({
        'transactions': [tx.to_dict() for tx in transactions],
        'count': len(transactions)
    }), 200

@wallets_bp.route('/wallets/<address>/alerts', methods=['POST'])
def create_alert(address):
    """Create a new alert for a wallet"""
    if not Web3.is_address(address):
        return jsonify({'error': 'Invalid Ethereum address'}), 400
    
    wallet = Wallet.query.filter_by(address=address).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    data = request.get_json()
    if not data or 'alert_type' not in data:
        return jsonify({'error': 'Alert type is required'}), 400
    
    alert = Alert(
        wallet_id=wallet.id,
        alert_type=data['alert_type'],
        threshold=data.get('threshold'),
        is_active=True
    )
    
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({
        'message': 'Alert created successfully',
        'alert': alert.to_dict()
    }), 201

@wallets_bp.route('/wallets/<address>/alerts', methods=['GET'])
def get_alerts(address):
    """Get all alerts for a wallet"""
    if not Web3.is_address(address):
        return jsonify({'error': 'Invalid Ethereum address'}), 400
    
    wallet = Wallet.query.filter_by(address=address).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    alerts = Alert.query.filter_by(wallet_id=wallet.id).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'count': len(alerts)
    }), 200

@wallets_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    db.session.delete(alert)
    db.session.commit()
    
    return jsonify({'message': 'Alert deleted successfully'}), 200
