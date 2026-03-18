# Wallet Watcher API Documentation

## Overview
This API monitors Ethereum wallets, tracks transactions, sends alerts, and provides enhanced analytics with Redis caching.

## Base URL

**Live (Render):**
```
https://wallet-watcher-api-1.onrender.com/api/v1
```

**Local development:**
```
http://localhost:5000/api/v1
```

## Authentication
All endpoints need an API key in the header.

**Example:**
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:5000/api/v1/wallets
```

---

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

---

### 2. Get Wallet Info
- **Method:** GET
- **URL:** `/wallets/{address}`
- **Description:** Get detailed information about a registered wallet.
- **Headers Required:** X-API-Key
- **Success Response (200):**
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

---

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

---

### 4. Get Wallet Transactions
**GET** `/wallets/{address}/transactions`

Get transaction history for a wallet.

**Path Parameters:**
- `address` - Ethereum wallet address

**Query Parameters:**
- `page` (optional, default: 1)
- `per_page` (optional, default: 20, max: 100)
- `type` (optional) - Filter by `incoming`, `outgoing`, or `all`

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

---

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

---

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

---

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

---

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

---

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

---

## Analytics Endpoints

Analytics endpoints provide enriched portfolio, gas, and token flow data. Responses are served from a Redis cache where possible to minimise RPC and external API calls. All endpoints require `X-API-Key`.

### 10. Get Portfolio
**GET** `/analytics/portfolio/{address}`

Full portfolio breakdown for an Ethereum address, combining ETH and ERC-20 balances with a live USD price feed.

**Path Parameters:**
- `address` - Ethereum wallet address (checksum-validated)

**Response (200):**
```json
{
  "address": "0x742d35Cc...",
  "eth": {
    "balance_wei": "1000000000000000000",
    "balance_eth": "1.0",
    "price_usd": 3200.00,
    "value_usd": 3200.00
  },
  "tokens": {
    "USDC": { "balance": "500000000", "value_usd": 500.00 },
    "USDT": { "balance": "0", "value_usd": 0 },
    "DAI":  { "balance": "0", "value_usd": 0 },
    "WETH": { "balance": "0", "value_usd": 0 }
  },
  "total_value_usd": 3700.00
}
```

**Cache TTL:** 300 seconds (5 minutes)

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:5000/api/v1/analytics/portfolio/0x742d35Cc...
```

**Error Responses:**
- 400: Invalid address
- 404: Wallet not found

---

### 11. Get Gas Spent
**GET** `/analytics/gas-spent/{address}`

Historical gas usage analysis for all outbound transactions sent by the address.

**Path Parameters:**
- `address` - Ethereum wallet address

**Query Parameters:**
- `days` (optional, default: 30, range: 1–365) - Time window for analysis

**Response (200):**
```json
{
  "address": "0x742d35Cc...",
  "days": 30,
  "transaction_count": 42,
  "total_gas_used": 882000,
  "total_gas_eth": "0.012345"
}
```

**Cache TTL:** 3600 seconds (1 hour) — historical data does not change.

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/analytics/gas-spent/0x742d35Cc...?days=30"
```

**Error Responses:**
- 400: Invalid address or days parameter
- 404: Wallet not found

---

### 12. Get Token Flows
**GET** `/analytics/token-flows/{address}`

Inbound and outbound ERC-20 transfer analysis, aggregated by token contract.

**Path Parameters:**
- `address` - Ethereum wallet address

**Query Parameters:**
- `days` (optional, default: 7, range: 1–365) - Time window for analysis

**Response (200):**
```json
{
  "address": "0x742d35Cc...",
  "days": 7,
  "inflows": {
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": {
      "transfer_count": 3,
      "volume_raw": "1500000000"
    }
  },
  "outflows": {
    "0xdAC17F958D2ee523a2206206994597C13D831ec7": {
      "transfer_count": 1,
      "volume_raw": "200000000"
    }
  }
}
```

**Cache TTL:** 1800 seconds (30 minutes)

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/analytics/token-flows/0x742d35Cc...?days=7"
```

**Error Responses:**
- 400: Invalid address or days parameter
- 404: Wallet not found

---

## Caching

Analytics responses are cached in Redis to reduce RPC and CoinGecko API calls. The cache is transparent to consumers — on a cache miss the API fetches fresh data automatically.

### TTL Strategy

| Data Type | TTL | Reason |
|-----------|-----|--------|
| ETH / token balances | 300s | Changes per block |
| Token flows | 1800s | Semi-historical |
| Gas history | 3600s | Historical — immutable |
| ETH price | 60s | Volatile |

### Cache Key Format

Keys follow the pattern `type:address:params` (e.g. `portfolio:0xabc:eth`), enabling pattern-based invalidation. To clear all cached data for a specific address, delete `portfolio:0xabc*`.

### Graceful Degradation

If the Redis cache is unavailable, all endpoints fall back to live RPC / CoinGecko data and return results without error — responses will be slower but functional.

### Performance

| Endpoint | Without cache | With cache |
|----------|--------------|------------|
| `/analytics/portfolio` | ~1200ms | ~5ms |
| `/analytics/gas-spent` | ~800ms | ~3ms |
| `/analytics/token-flows` | ~1500ms | ~4ms |

---

## Rate Limits

100 requests per hour per API key.
