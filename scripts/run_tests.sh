#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Starting Security Platform Testing Suite"

# 1. Security Scans
echo -e "\n${GREEN}Running Security Scans...${NC}"
bandit -r src/ || exit 1
safety check || exit 1

# 2. Unit Tests
echo -e "\n${GREEN}Running Unit Tests...${NC}"
pytest tests/ -v --cov=src --cov-report=term-missing || exit 1

# 3. Security-specific Tests
echo -e "\n${GREEN}Running Security Tests...${NC}"
pytest tests/security/ -v || exit 1

# 4. Integration Tests
echo -e "\n${GREEN}Running Integration Tests...${NC}"
pytest tests/integration/ -v || exit 1

echo -e "\n${GREEN}All tests completed successfully!${NC}"