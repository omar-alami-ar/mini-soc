import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="session")
def test_config():
    """Test configuration loaded from environment variables."""
    return {
        "dashboard_url": os.getenv("WAZUH_DASHBOARD_URL", "https://localhost:443"),
        "dashboard_username": os.getenv("WAZUH_DASHBOARD_USERNAME", "kibanaserver"),
        "dashboard_password": os.getenv("WAZUH_DASHBOARD_PASSWORD", ""),
        "manager_api_url": os.getenv("WAZUH_MANAGER_API_URL", "https://localhost:55000"),
        "manager_username": os.getenv("WAZUH_MANAGER_USERNAME", "wazuh-wui"),
        "manager_password": os.getenv("WAZUH_MANAGER_PASSWORD", ""),
        "indexer_url": os.getenv("WAZUH_INDEXER_URL", "https://localhost:9200"),
        "indexer_username": os.getenv("WAZUH_INDEXER_USERNAME", "admin"),
        "indexer_password": os.getenv("WAZUH_INDEXER_PASSWORD", ""),
        "headless": os.getenv("SELENIUM_HEADLESS", "true").lower() == "true",
        "timeout": int(os.getenv("SELENIUM_TIMEOUT", "30")),
        "implicit_wait": int(os.getenv("SELENIUM_IMPLICIT_WAIT", "10"))
    }

@pytest.fixture(scope="function")
def driver(test_config):
    """Selenium WebDriver fixture with Chrome configuration."""
    chrome_options = Options()
    
    if test_config["headless"]:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # For HTTPS testing with self-signed certificates
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    chrome_options.add_argument("--ignore-ssl-errors")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set implicit wait
    driver.implicitly_wait(test_config["implicit_wait"])
    
    yield driver
    
    # Cleanup
    driver.quit()

@pytest.fixture(scope="session")
def api_session(test_config):
    """Requests session for API testing with proper SSL handling."""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # For self-signed certificates in testing
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    return session 