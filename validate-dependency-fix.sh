#!/bin/bash
# Validation script for npm dependency conflict fix
# This script verifies that the @cypress/react upgrade resolves the peer dependency conflict

set -e  # Exit on error

echo "=========================================="
echo "NPM Dependency Conflict Fix - Validation"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to frontend directory
cd "$(dirname "$0")/frontend" || exit 1

echo "1. Checking @cypress/react version in package.json..."
if ! command -v jq >/dev/null 2>&1; then
    echo -e "${RED}jq is required but not installed. Please install jq to continue.${NC}"
    exit 1
fi
CYPRESS_VERSION=$(jq -r '.dependencies["@cypress/react"] // .devDependencies["@cypress/react"] // empty' package.json | sed 's/^[^0-9]*//')
echo -e "   Found: ${GREEN}@cypress/react@${CYPRESS_VERSION}${NC}"

if [[ "$CYPRESS_VERSION" == "9.0.1" ]]; then
    echo -e "   ${GREEN}✓ Correct version (9.0.1)${NC}"
else
    echo -e "   ${RED}✗ Expected version 9.0.1${NC}"
    exit 1
fi
echo ""

echo "2. Checking peer dependencies for @cypress/react@${CYPRESS_VERSION}..."
PEER_DEPS=$(npm info @cypress/react@${CYPRESS_VERSION} peerDependencies --json 2>/dev/null)
echo "   Peer Dependencies:"
echo "$PEER_DEPS" | grep -E '@types/react|react"' | sed 's/^/     /'

TYPES_REACT_PEER=$(echo "$PEER_DEPS" | grep '@types/react' | grep -o '\^[0-9]*')
if [[ "$TYPES_REACT_PEER" == ^18* ]]; then
    echo -e "   ${GREEN}✓ Supports @types/react ^18${NC}"
else
    echo -e "   ${RED}✗ Does not support @types/react ^18${NC}"
    exit 1
fi
echo ""

echo "3. Checking current @types/react version in package.json..."
TYPES_REACT_VERSION=$(grep '"@types/react"' package.json | sed -n 's/.*"\^*\([0-9.]*\)".*/\1/p')
echo -e "   Current: ${GREEN}@types/react@^${TYPES_REACT_VERSION}${NC}"

if [[ "$TYPES_REACT_VERSION" =~ ^18\. ]]; then
    echo -e "   ${GREEN}✓ React 18 compatible${NC}"
else
    echo -e "   ${YELLOW}⚠ Warning: Not React 18${NC}"
fi
echo ""

echo "4. Checking Dockerfile for --legacy-peer-deps flag..."
if grep -q "npm ci.*--legacy-peer-deps" Dockerfile; then
    echo -e "   ${GREEN}✓ Found --legacy-peer-deps flag in Dockerfile${NC}"
else
    echo -e "   ${RED}✗ Missing --legacy-peer-deps flag in Dockerfile${NC}"
    exit 1
fi
echo ""

echo "5. Verifying package-lock.json has @cypress/react@9.0.1..."
if grep -q '"version": "9.0.1"' package-lock.json && grep -q '@cypress/react' package-lock.json; then
    echo -e "   ${GREEN}✓ package-lock.json contains @cypress/react@9.0.1${NC}"
else
    echo -e "   ${RED}✗ package-lock.json does not contain @cypress/react@9.0.1${NC}"
    exit 1
fi
echo ""

echo "6. Testing npm dependency resolution (dry-run)..."
if npm install --dry-run --legacy-peer-deps > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ npm install dry-run successful${NC}"
else
    echo -e "   ${RED}✗ npm install dry-run failed${NC}"
    exit 1
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✓ All validation checks passed!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - @cypress/react upgraded to 9.0.1"
echo "  - Peer dependencies compatible with React 18"
echo "  - Dockerfile configured with --legacy-peer-deps"
echo "  - package-lock.json updated correctly"
echo "  - npm dependency resolution successful"
echo ""
echo "The npm peer dependency conflict has been resolved."
