# .github/workflows/security-scan.yml
name: Security Scanning Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # Daily scan
  workflow_dispatch:      # Manual trigger

env:
  PYTHON_VERSION: '3.9'
  AZURE_FUNCTIONAPP_PACKAGE_PATH: '.'

jobs:
  security_scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Create virtual environment
        run: |
          python -m venv .venv
          source .venv/bin/activate
          echo "VIRTUAL_ENV=$VIRTUAL_ENV" >> $GITHUB_ENV
          echo "$VIRTUAL_ENV/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          # Install core dependencies first
          pip install \
            azure-functions==1.17.0 \
            azure-identity==1.19.0 \
            azure-mgmt-resource==23.0.1 \
            azure-cosmos==4.5.1 \
            azure-storage-blob==12.19.0 \
            aiohttp==3.9.1 \
            cryptography==41.0.1
          
          # Install testing and development dependencies
          pip install \
            pytest==7.4.3 \
            pytest-asyncio==0.21.1 \
            pytest-cov==4.1.0 \
            python-dateutil==2.8.2 \
            PyYAML==6.0.1

      - name: Configure Azure credentials
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Set up environment variables
        run: |
          echo "COSMOS_DB_CONNECTION_STRING=${{ secrets.COSMOS_DB_CONNECTION_STRING }}" >> $GITHUB_ENV
          echo "COSMOS_DB_DATABASE_NAME=${{ secrets.COSMOS_DB_DATABASE_NAME }}" >> $GITHUB_ENV
          echo "COSMOS_DB_CONTAINER_NAME=${{ secrets.COSMOS_DB_CONTAINER_NAME }}" >> $GITHUB_ENV
          echo "NVD_API_KEY=${{ secrets.NVD_API_KEY }}" >> $GITHUB_ENV
          echo "PYTHONPATH=${{ github.workspace }}" >> $GITHUB_ENV

      - name: Initialize logging
        run: |
          python -c "
          import logging
          import os
          
          logging.basicConfig(
              level=logging.INFO,
              format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
              handlers=[
                  logging.StreamHandler(),
                  logging.FileHandler('security_scan.log')
              ]
          )
          logger = logging.getLogger('security_scan')
          logger.info('Security scanning environment initialized')
          "

      - name: Run dependency scan
        run: |
          python -c "
          import asyncio
          import logging
          from src.scanners.dependency_scanner import DependencyScanner
          
          async def scan_dependencies():
              scanner = DependencyScanner()
              dependencies = [
                  {'name': 'azure-functions', 'version': '1.17.0'},
                  {'name': 'azure-identity', 'version': '1.19.0'},
                  {'name': 'azure-cosmos', 'version': '4.5.1'}
              ]
              results = await scanner.scan(dependencies)
              return results
          
          results = asyncio.run(scan_dependencies())
          logger = logging.getLogger('security_scan')
          logger.info(f'Dependency scan completed: {results}')
          "

      - name: Run compliance scan
        run: |
          python -c "
          import asyncio
          import logging
          from src.scanners.compliance_scanner import ComplianceScanner
          
          async def scan_compliance():
              scanner = ComplianceScanner()
              config = {
                  'password_policy': {
                      'min_length': 12,
                      'require_special_chars': True
                  },
                  'encryption': {
                      'require_tls': True,
                      'require_at_rest': True
                  },
                  'access_control': {
                      'require_mfa': True,
                      'require_rbac': True
                  }
              }
              results = await scanner.scan(config)
              return results
          
          results = asyncio.run(scan_compliance())
          logger = logging.getLogger('security_scan')
          logger.info(f'Compliance scan completed: {results}')
          "

      - name: Run full security scan
        if: success()
        run: |
          python -c "
          import asyncio
          import json
          import logging
          from src.scanners.scanning_service import ScanningService
          
          async def run_full_scan():
              scanner = ScanningService()
              results = await scanner.run_scan()
              
              with open('scan_results.json', 'w') as f:
                  json.dump(results, f, indent=2)
              
              return results
          
          results = asyncio.run(run_full_scan())
          logger = logging.getLogger('security_scan')
          logger.info(f'Full security scan completed')
          
          if results.get('status') == 'failed':
              logger.error(f'Scan failed: {results.get("error")}')
              exit(1)
          "

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-scan-results
          path: |
            scan_results.json
            security_scan.log
          retention-days: 14

  notify:
    needs: security_scan
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Check scan status
        run: |
          if [ "${{ needs.security_scan.result }}" == "success" ]; then
            echo "Security scan completed successfully"
          else
            echo "Security scan failed"
            exit 1
          fi