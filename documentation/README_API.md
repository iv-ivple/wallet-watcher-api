# Wallet Watcher API Documentation

## Overview
This API monitors Ethereum wallets, tracks transactions, sends alerts, and provides enhanced analytics with optional Redis caching.

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

There are **two separate credentials** in this API — don't confuse them.

### 1. API keys (`X-API-Key`)
Every endpoint below except `/health` and key creation itself requires an API key in the header:
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:5000/api/v1/wallets
```
API keys are issued via `POST /api-keys` (see below) and stored in the database. They don't expire and aren't scoped — any valid, active key can call any protected endpoint.

### 2. Admin secret (`X-Admin-Secret`)
Creating a *new* API key is itself a protected action, and it can't reasonably require an API key (you'd need one to get one). Instead it requires a separate, single shared secret set as the `ADMIN_SECRET` environment variable on the server. This is not stored in the database and isn't visible through any API response — you'll need to get it from whoever manages the deployment (or `.env` locally).

---

## Endpoints

### 1. Register Wallet
- **Method:** POST
- **URL:** `/wallets`
- **Description:** Register a new wallet to monitor
- **Headers Required:** `X-API-Key`
- **Request Body:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
  "label": "My Main Wallet"
}
```
- **Success Response (201):**
```json
{
  "message": "Wallet registered successfully",
  "wallet": {
    "id": 1,
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "label": "My Main Wallet",
    "balance": "1000000000000000000",
    "last_monitored": null,
    "created_at": "2026-07-01T10:30:00"
  }
}
```
Note: `balance` is the wei balance as a string, captured at registration time — it is not automatically refreshed on every read; the background monitor updates it periodically.
- **Error Responses:**
  - 400: Missing `address` field, or address fails `Web3.is_address()` / checksum validation
  - 401: Missing or invalid `X-API-Key`
  - 409: Wallet already registered
  - 500: Server error (e.g. RPC call to fetch initial balance failed)

---

### 2. Get Wallet Info
- **Method:** GET
- **URL:** `/wallets/{address}`
- **Description:** Get the stored record for a registered wallet.
- **Headers Required:** `X-API-Key`
- **Success Response (200):**
```json
{
  "wallet": {
    "id": 1,
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "label": "My Main Wallet",
    "balance": "1000000000000000000",
    "last_monitored": "2026-07-01T10:35:00",
    "created_at": "2026-07-01T10:30:00"
  }
}
```
This returns the last-known stored balance from the database, not a live on-chain lookup. There is no separate wei/eth breakdown and no transaction count in this response — for transaction history use endpoint 4.
- **Error Responses:**
  - 400: Invalid address format
  - 401: Missing or invalid `X-API-Key`
  - 404: Wallet not registered

---

### 3. List All Wallets
**GET** `/wallets`

List all registered wallets. **There is currently no pagination** — this returns every registered wallet in one response.

**Response (200):**
```json
{
  "wallets": [
    {
      "id": 1,
      "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
      "label": "My Main Wallet",
      "balance": "1000000000000000000",
      "last_monitored": "2026-07-01T10:35:00",
      "created_at": "2026-07-01T10:30:00"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl -H "X-API-Key: your_key" "http://localhost:5000/api/v1/wallets"
```

---

### 4. Get Wallet Transactions
**GET** `/wallets/{address}/transactions`

Get transaction history for a wallet. **There is currently no pagination and no `type` filter** — this returns every stored transaction for the wallet, newest first.

**Path Parameters:**
- `address` - Ethereum wallet address

**Response (200):**
```json
{
  "transactions": [
    {
      "id": 1,
      "wallet_id": 1,
      "tx_hash": "0xabc123...",
      "from_address": "0x123...",
      "to_address": "0x742d35Cc...",
      "value": "1000000000000000000",
      "timestamp": "2026-07-01T10:00:00",
      "block_number": 18500000,
      "status": "success"
    }
  ],
  "count": 1
}
```
Note field names: `from_address` / `to_address`, not `from` / `to`. `gas_used` is stored on the transaction model but is not currently included in this response.

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/wallets/0x742d35Cc.../transactions"
```

**Error Responses:**
- 400: Invalid address
- 401: Missing or invalid `X-API-Key`
- 404: Wallet not found

---

### 5. Create Balance Alert
**POST** `/wallets/{address}/alerts`

Create a new balance alert for a wallet.

**Headers Required:** `X-API-Key`

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
    "wallet_id": 1,
    "alert_type": "balance_above",
    "threshold": "2000000000000000000",
    "is_active": true,
    "created_at": "2026-07-01T11:00:00"
  }
}
```
Note: `last_triggered` exists as a database column but is not currently included in this response.

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "balance_above", "threshold": "2000000000000000000"}' \
  http://localhost:5000/api/v1/wallets/0x742d35Cc.../alerts
```

**Error Responses:**
- 400: Missing `alert_type`, or wallet address is invalid
- 401: Missing or invalid `X-API-Key`
- 404: Wallet not found

---

### 6. Get Wallet Alerts
**GET** `/wallets/{address}/alerts`

Get all alerts for a wallet.

**Headers Required:** `X-API-Key`

**Response (200):**
```json
{
  "alerts": [
    {
      "id": 1,
      "wallet_id": 1,
      "alert_type": "balance_above",
      "threshold": "2000000000000000000",
      "is_active": true,
      "created_at": "2026-07-01T11:00:00"
    }
  ],
  "count": 1
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

**Headers Required:** `X-API-Key`

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
- 401: Missing or invalid `X-API-Key`
- 404: Alert not found

---

### 8. Create API Key
**POST** `/api-keys`

Generate a new API key for authentication. **This is protected by the admin secret, not an API key** (see Authentication above).

**Headers Required:** `X-Admin-Secret`

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

**⚠️ Important:** Save this key! It's not retrievable again — the API never returns an existing key's value after creation.

**Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Admin-Secret: your_admin_secret" \
  -d '{"name": "My App Key"}' \
  http://localhost:5000/api/v1/api-keys
```

**Error Responses:**
- 401: Missing or incorrect `X-Admin-Secret`

---

### 9. Health Check
**GET** `/health`

Check API health status. **This path has no `/api/v1` prefix** — it's `https://.../health`, not `https://.../api/v1/health`.

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

Analytics endpoints provide portfolio, gas, and token-flow data pulled live from an Ethereum RPC provider (and CoinGecko for pricing), optionally cached in Redis. **All analytics endpoints require `X-API-Key`.** Unlike the wallet endpoints, these work for *any* valid Ethereum address — the address does not need to be registered via `POST /wallets` first.

### 10. Get Portfolio
**GET** `/analytics/portfolio/{address}`

ETH and known-ERC-20 token balances for an address, with a live USD price for ETH (token USD pricing is not currently implemented — see response shape below).

**Path Parameters:**
- `address` - Ethereum wallet address (checksum-validated)

**Response (200):**
```json
{
  "address": "0x742d35Cc...",
  "cached": false,
  "holdings": [
    { "token": "ETH", "balance": 1.5, "price_usd": 3200.00, "value_usd": 4800.00 },
    { "token": "USDC", "balance": 500.0, "price_usd": null, "value_usd": null }
  ],
  "token_count": 2,
  "total_value_usd": 4800.00
}
```
`holdings` is a flat list, ETH first. Only ETH currently gets a real `price_usd` (via CoinGecko); ERC-20 tokens (USDC, USDT, DAI, WETH) report `price_usd: null` and are excluded from `total_value_usd` — token USD pricing isn't wired up yet. Small dust balances (<0.001) are omitted per-token.

**Cache TTL:** 300 seconds (5 minutes), cache key `portfolio:{address_lowercase}`.

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:5000/api/v1/analytics/portfolio/0x742d35Cc...
```

**Error Responses:**
- 400: Invalid address
- 401: Missing or invalid `X-API-Key`
- 500: Upstream RPC or price-feed error

---

### 11. Get Gas Spent
**GET** `/analytics/gas-spent/{address}`

**Despite the name, this does not currently compute actual gas spent.** It reports the address's outbound transaction count (nonce) as a proxy, plus the block range considered. Real gas accounting would require an indexer (e.g. The Graph) and isn't implemented.

**Path Parameters:**
- `address` - Ethereum wallet address

**Query Parameters:**
- `days` (optional, default: 30) — silently clamped to the range 1–365; no error is returned for out-of-range or non-numeric values, it just falls back to the default/clamped value.

**Response (200):**
```json
{
  "address": "0x742d35Cc...",
  "cached": false,
  "period_days": 30,
  "total_transactions_sent": 42,
  "current_block": 21050000,
  "from_block": 20834000,
  "note": "Full gas history requires The Graph API. Add GRAPH_API_KEY to .env for detailed breakdown."
}
```

**Cache TTL:** 3600 seconds (1 hour), cache key `gas:{address_lowercase}:{days}d`.

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/analytics/gas-spent/0x742d35Cc...?days=30"
```

**Error Responses:**
- 400: Invalid address
- 401: Missing or invalid `X-API-Key`
- 500: Upstream RPC error

---

### 12. Get Token Flows
**GET** `/analytics/token-flows/{address}`

Inbound and outbound ERC-20 transfer analysis via `eth_getLogs`, aggregated by token contract address.

**Path Parameters:**
- `address` - Ethereum wallet address

**Query Parameters:**
- `days` (optional, default: 7) — silently clamped to the range **1–30** (deliberately smaller than gas-spent's range, since `eth_getLogs` queries are expensive)

**Response (200):**
```json
{
  "address": "0x742d35Cc...",
  "cached": false,
  "period_days": 7,
  "inbound_count": 3,
  "outbound_count": 1,
  "inflows": [
    { "token_address": "0xA0b8...", "transfer_count": 3, "total_raw": 1500000000 }
  ],
  "outflows": [
    { "token_address": "0xdAC1...", "transfer_count": 1, "total_raw": 200000000 }
  ]
}
```
`inflows`/`outflows` are lists (not keyed objects), and `total_raw` is in the token's smallest unit (no decimal adjustment applied).

**⚠️ Known limitation:** on Alchemy's free/lower tiers, `eth_getLogs` over even the default 7-day block range can be rejected outright (`400 Client Error` from Alchemy, surfaced here as a 500). If you hit this, try a smaller `days` value or upgrade the Alchemy plan tier.

**Cache TTL:** 1800 seconds (30 minutes), cache key `flows:{address_lowercase}:{days}d`.

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  "http://localhost:5000/api/v1/analytics/token-flows/0x742d35Cc...?days=7"
```

**Error Responses:**
- 400: Invalid address
- 401: Missing or invalid `X-API-Key`
- 500: Upstream RPC error (including block-range rejections, see above)

---

## Caching

Analytics responses are cached in Redis when a working `REDIS_URL` is configured, to reduce RPC and CoinGecko calls. **If `REDIS_URL` isn't set, or Redis is unreachable, every analytics call silently falls back to uncached (live) behavior** — slower, but functional, with `"cached": false` on every response.

### TTL Strategy

| Endpoint | TTL | Reason |
|-----------|-----|--------|
| `/analytics/portfolio` | 300s | Balances change per block |
| `/analytics/token-flows` | 1800s | Semi-historical |
| `/analytics/gas-spent` | 3600s | Effectively historical (nonce-based) |

### Cache Key Format

Keys follow the pattern `{type}:{address_lowercase}[:{days}d]`, e.g. `portfolio:0x742d35cc...`, `gas:0x742d35cc...:30d`, `flows:0x742d35cc...:7d`.

### Graceful Degradation

If Redis is unavailable, all endpoints fall back to live RPC / CoinGecko data and return results without error — responses will be slower but functional. This is also the default behavior if `REDIS_URL` is simply never set.

---

## Rate Limits

100 requests per hour, applied **per client IP address** — not per API key. Multiple API keys used from the same IP share the same limit.
