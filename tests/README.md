# Wazuh SOC Testing Suite

This directory contains comprehensive tests for validating the Wazuh SOC deployment, including Selenium-based UI tests and API health probes.

## 🧪 Test Categories

### 1. UI Tests (`test_dashboard_ui.py`)
- **HTTPS Accessibility**: Validates the dashboard is reachable over HTTPS
- **Page Title Validation**: Ensures proper page titles are displayed
- **Login Form Elements**: Verifies all required login form components are present
- **Programmatic Login**: Optional test for automated login using test credentials
- **Dashboard Responsiveness**: Basic interaction and content validation

### 2. API Health Tests (`test_api_health.py`)
- **Manager API Health**: Tests Wazuh manager API endpoints (port 55000)
- **Indexer API Health**: Validates OpenSearch/Wazuh indexer (port 9200)
- **Dashboard API**: Checks dashboard API accessibility
- **SSL Validation**: Ensures all endpoints use HTTPS
- **Response Time Monitoring**: Performance validation

### 3. Integration Tests (`test_integration.py`)
- **System Connectivity**: End-to-end component communication
- **API Consistency**: Response format validation across services
- **SSL Certificate Validation**: Security configuration checks
- **System Health Summary**: Comprehensive health scoring and recommendations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
python run_tests.py --install-deps

# Or manually
pip install -r requirements-test.txt
```

### 2. Configure Environment
```bash
# Copy example configuration
cp env.example .env

# Edit .env with your actual Wazuh deployment details
nano .env
```

### 3. Run Tests
```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --ui          # UI tests only
python run_tests.py --api         # API tests only
python run_tests.py --integration # Integration tests only

# Quick health check
python run_tests.py --health

# Quick tests (skip optional/slow)
python run_tests.py --quick
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Dashboard Configuration
WAZUH_DASHBOARD_URL=https://your-wazuh-dashboard:443
WAZUH_DASHBOARD_USERNAME=kibanaserver
WAZUH_DASHBOARD_PASSWORD=your-dashboard-password

# Manager API Configuration
WAZUH_MANAGER_API_URL=https://your-wazuh-manager:55000
WAZUH_MANAGER_USERNAME=wazuh-wui
WAZUH_MANAGER_PASSWORD=your-manager-password

# Indexer API Configuration
WAZUH_INDEXER_URL=https://your-wazuh-indexer:9200
WAZUH_INDEXER_USERNAME=admin
WAZUH_INDEXER_PASSWORD=your-indexer-password

# Selenium Configuration
SELENIUM_HEADLESS=true          # Run browser in headless mode
SELENIUM_TIMEOUT=30             # Page load timeout in seconds
SELENIUM_IMPLICIT_WAIT=10       # Element wait timeout
```

### Network Configuration

Ensure your test environment can reach:
- **Dashboard**: Port 443 (HTTPS)
- **Manager API**: Port 55000 (HTTPS)
- **Indexer API**: Port 9200 (HTTPS)

## 🔧 Test Execution Options

### Using pytest directly
```bash
# Run specific test file
pytest tests/test_dashboard_ui.py -v

# Run specific test class
pytest tests/test_dashboard_ui.py::TestWazuhDashboardUI -v

# Run specific test method
pytest tests/test_dashboard_ui.py::TestWazuhDashboardUI::test_dashboard_https_accessible -v

# Run with markers
pytest -m "not optional"  # Skip optional tests
pytest -m "ui"            # Run only UI tests
pytest -m "api"           # Run only API tests
```

### Using the test runner
```bash
# Show help
python run_tests.py --help

# Install dependencies
python run_tests.py --install-deps

# Run health check
python run_tests.py --health

# Run all tests
python run_tests.py --all
```

## 📊 Test Results

Test results are automatically generated in the `test-results/` directory:

- **HTML Reports**: Detailed test results with pass/fail status
- **Console Output**: Real-time test execution information
- **Health Scores**: Overall system health percentages

## 🐛 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # The webdriver-manager will automatically download ChromeDriver
   # If you encounter issues, ensure Chrome is installed
   ```

2. **SSL Certificate Errors**
   ```bash
   # Tests are configured to handle self-signed certificates
   # Ensure your .env URLs use HTTPS
   ```

3. **Connection Timeouts**
   ```bash
   # Increase timeout values in .env
   SELENIUM_TIMEOUT=60
   SELENIUM_IMPLICIT_WAIT=20
   ```

4. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   python run_tests.py --install-deps
   ```

### Debug Mode

For debugging, run tests with verbose output:
```bash
pytest -v -s --tb=long
```

## 🔒 Security Notes

- **Credentials**: Never commit `.env` files with real passwords
- **Test Accounts**: Use dedicated test accounts, not production admin accounts
- **Network Access**: Tests should run from a secure, controlled environment
- **SSL Verification**: Tests bypass SSL verification for self-signed certificates in testing

## 📝 Adding New Tests

### UI Test Example
```python
def test_new_feature(self, driver, test_config):
    """Test description."""
    try:
        driver.get(test_config["dashboard_url"])
        # Your test logic here
        assert condition, "Failure message"
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")
```

### API Test Example
```python
def test_new_api_endpoint(self, api_session, test_config):
    """Test description."""
    try:
        response = api_session.get(f"{test_config['manager_api_url']}/new-endpoint")
        assert response.status_code == 200
        data = response.json()
        # Validate response data
    except Exception as e:
        pytest.fail(f"API test failed: {str(e)}")
```

## 🏗️ CI/CD Integration

### GitHub Actions Example
```yaml
name: Wazuh Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: python run_tests.py --install-deps
      - name: Run tests
        run: python run_tests.py --quick
        env:
          WAZUH_DASHBOARD_URL: ${{ secrets.WAZUH_DASHBOARD_URL }}
          WAZUH_DASHBOARD_USERNAME: ${{ secrets.WAZUH_DASHBOARD_USERNAME }}
          WAZUH_DASHBOARD_PASSWORD: ${{ secrets.WAZUH_DASHBOARD_PASSWORD }}
          # ... other environment variables
```

## 📚 Additional Resources

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Wazuh Documentation](https://documentation.wazuh.com/)
- [OpenSearch Documentation](https://opensearch.org/docs/)

## 🤝 Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Add appropriate docstrings and comments
3. Use the provided fixtures (`driver`, `api_session`, `test_config`)
4. Handle exceptions gracefully with `pytest.fail()`
5. Add appropriate test markers if needed
6. Update this README with new test information 