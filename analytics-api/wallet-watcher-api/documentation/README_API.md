# Wallet Watcher API Documentation

## Overview
This API monitors Ethereum wallets, tracks transactions, sends alerts).

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
All endpoints need an API key in the header.

**Example:**
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:5000/api/v1/wallets
```

## Endpoints

### 1. Register Wallet
- **Method:** POST
- **URL:** `/wallets`
- **Description:** Register a new wallet to monitor
- **Headers Required:** X-API-Key
- **Request Body:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "label": "My Main Wallet"
}
```
- **Success Response (201):**
```json
{
  "message": "Wallet registered successfully",
  "wallet": {
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "label": "My Main Wallet",
    "created_at": "2024-12-21T10:30:00",
    "current_balance": "1000000000000000000"
  }
}
```
- **Error Responses:**
  - 400: Invalid address
  - 409: Wallet already registered
  - 500: Server error

### 2. Get Wallet Info
- **Method:** GET
- **URL:** `/wallets/{address}`
- **Description:** Get detailed information about a registered wallet.
- **Headers Required:** X-API-Key
- **Success Response (201):**
```json
{
  "wallet": {
    "address": "0x742d35Cc...",
    "label": "My Main Wallet",
    "last_checked": "2024-12-21T10:35:00"
  },
  "balance": {
    "wei": "1000000000000000000",
    "eth": "1.0"
  },
  "transaction_count": 5
}
```


### 3. List All Wallets
**GET** `/wallets`

List all registered wallets with pagination.

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 20, max: 100) - Items per page

**Response (200):**
```json
{
  "wallets": [
    {
      "address": "0x742d35Cc...",
      "label": "My Main Wallet",
      "created_at": "2024-12-21T10:30:00",
      "current_balance": "1000000000000000000"
    }
  ],
  "total": 5,
  "page": 1,
  "pages": 1
}
```

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/wallets?page=1&per_page=20"
```

### 4. Get Wallet Transactions
**GET** `/wallets/{address}/transactions`

Get transaction history for a wallet.

**Path Parameters:**
- `address` - Ethereum wallet address

**Query Parameters:**
- `page` (optional, default: 1)
- `per_page` (optional, default: 20, max: 100)
- `type` (optional) - Filter by 'incoming', 'outgoing', or 'all'

**Response (200):**
```json
{
  "transactions": [
    {
      "tx_hash": "0xabc123...",
      "block_number": 18500000,
      "timestamp": "2024-12-21T10:00:00",
      "from": "0x123...",
      "to": "0x742d35Cc...",
      "value": "1000000000000000000",
      "gas_used": 21000,
      "status": "success"
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/wallets/0x742d35Cc.../transactions?type=incoming"
```

**Error Responses:**
- 400: Invalid address
- 404: Wallet not found


### 5. Create Balance Alert
**POST** `/wallets/{address}/alerts`

Create a new balance alert for a wallet.

**Path Parameters:**
- `address` - Ethereum wallet address

**Request Body:**
```json
{
  "alert_type": "balance_above",
  "threshold": "2000000000000000000"
}
```

**Alert Types:**
- `balance_above` - Alert when balance goes above threshold
- `balance_below` - Alert when balance goes below threshold

**Note:** Threshold must be in Wei (1 ETH = 1000000000000000000 Wei)

**Response (201):**
```json
{
  "message": "Alert created successfully",
  "alert": {
    "id": 1,
    "alert_type": "balance_above",
    "threshold": "2000000000000000000",
    "is_active": true,
    "created_at": "2024-12-21T11:00:00",
    "last_triggered": null
  }
}
```

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "balance_above", "threshold": "2000000000000000000"}' \
  http://localhost:5000/api/v1/wallets/0x742d35Cc.../alerts
```

**Error Responses:**
- 400: Invalid alert_type or threshold
- 404: Wallet not found

### 6. Get Wallet Alerts
**GET** `/wallets/{address}/alerts`

Get all alerts for a wallet.

**Path Parameters:**
- `address` - Ethereum wallet address

**Response (200):**
```json
{
  "alerts": [
    {
      "id": 1,
      "alert_type": "balance_above",
      "threshold": "2000000000000000000",
      "is_active": true,
      "created_at": "2024-12-21T11:00:00",
      "last_triggered": "2024-12-21T12:00:00"
    }
  ]
}
```

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:5000/api/v1/wallets/0x742d35Cc.../alerts
```

### 7. Delete Alert
**DELETE** `/alerts/{alert_id}`

Delete an alert by ID.

**Path Parameters:**
- `alert_id` - Alert ID (integer)

**Response (200):**
```json
{
  "message": "Alert deleted successfully"
}
```

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  -X DELETE \
  http://localhost:5000/api/v1/alerts/1
```

**Error Responses:**
- 404: Alert not found

### 8. Create API Key
**POST** `/api-keys`

Generate a new API key for authentication.

**Request Body:**
```json
{
  "name": "My App Key"
}
```

**Response (201):**
```json
{
  "message": "API key created successfully",
  "api_key": "xKj9mN4pQ7wR2tY8vB5nC3hL6fG1sD0a",
  "name": "My App Key"
}
```

**⚠️ Important:** Save this key! You won't be able to see it again.

**Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "My App Key"}' \
  http://localhost:5000/api/v1/api-keys
```

**Note:** In production, you'd want to protect this endpoint with a master password or admin authentication.

### 9. Health Check
**GET** `/health`

Check API health status.

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

**Note:** This endpoint does NOT require authentication.
```


## Rate Limits
Rate limiting 100 requests per hour


