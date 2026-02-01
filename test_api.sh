#!/bin/bash

# Wallet Watcher API Testing Script
# Replace these with your actual values
API_KEY="ITxgCHF_0OGpdFEKDkuGphTWLRLfWCtOdfaoAnDYhYytj7zee6dEHcgep6S2qzZh"
BASE_URL="https://wallet-watcher-api.onrender.com"

# Test wallet address (use a real Ethereum address for testing)
TEST_WALLET="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "Wallet Watcher API Testing"
echo "========================================"
echo ""

# Test 1: Health Check (No Auth)
echo -e "${BLUE}Test 1: Health Check${NC}"
echo "GET /health"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/health
echo -e "${GREEN}---${NC}\n"

# Test 2: Register New Wallet
echo -e "${BLUE}Test 2: Register New Wallet${NC}"
echo "POST /api/v1/wallets"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"address\":\"$TEST_WALLET\",\"label\":\"Test Wallet\"}" \
  $BASE_URL/api/v1/wallets
echo -e "${GREEN}---${NC}\n"

# Test 3: List All Wallets
echo -e "${BLUE}Test 3: List All Wallets${NC}"
echo "GET /api/v1/wallets"
curl -s -w "\nStatus: %{http_code}\n" \
  -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/v1/wallets
echo -e "${GREEN}---${NC}\n"

# Test 4: Get Wallet Details
echo -e "${BLUE}Test 4: Get Wallet Details${NC}"
echo "GET /api/v1/wallets/$TEST_WALLET"
curl -s -w "\nStatus: %{http_code}\n" \
  -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/v1/wallets/$TEST_WALLET
echo -e "${GREEN}---${NC}\n"

# Test 5: Get Wallet Transactions
echo -e "${BLUE}Test 5: Get Wallet Transactions${NC}"
echo "GET /api/v1/wallets/$TEST_WALLET/transactions"
curl -s -w "\nStatus: %{http_code}\n" \
  -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/v1/wallets/$TEST_WALLET/transactions
echo -e "${GREEN}---${NC}\n"

# Test 6: Create Alert
echo -e "${BLUE}Test 6: Create Alert${NC}"
echo "POST /api/v1/wallets/$TEST_WALLET/alerts"
curl -s -w "\nStatus: %{http_code}\n" \
  -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"alert_type":"balance_change","threshold":"0.1","notification_method":"email"}' \
  $BASE_URL/api/v1/wallets/$TEST_WALLET/alerts
echo -e "${GREEN}---${NC}\n"

# Test 7: List Wallet Alerts
echo -e "${BLUE}Test 7: List Wallet Alerts${NC}"
echo "GET /api/v1/wallets/$TEST_WALLET/alerts"
curl -s -w "\nStatus: %{http_code}\n" \
  -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/v1/wallets/$TEST_WALLET/alerts
echo -e "${GREEN}---${NC}\n"

# Test 8: Delete Alert (you'll need to replace ALERT_ID with actual ID from test 7)
echo -e "${BLUE}Test 8: Delete Alert${NC}"
echo "DELETE /api/v1/alerts/{alert_id}"
echo -e "${RED}NOTE: Replace ALERT_ID with actual ID from Test 7${NC}"
read -p "Enter Alert ID to delete (or press Enter to skip): " ALERT_ID
if [ ! -z "$ALERT_ID" ]; then
  curl -s -w "\nStatus: %{http_code}\n" \
    -X DELETE \
    -H "X-API-Key: $API_KEY" \
    $BASE_URL/api/v1/alerts/$ALERT_ID
else
  echo "Skipped"
fi
echo -e "${GREEN}---${NC}\n"

echo "========================================"
echo "Testing Complete!"
echo "========================================"
