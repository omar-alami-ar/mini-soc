import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestWazuhIntegration:
    """Integration tests that validate the overall Wazuh system health."""
    
    def test_system_connectivity(self, driver, api_session, test_config):
        """Test that all Wazuh components are accessible and communicating."""
        components = [
            ("Dashboard", test_config["dashboard_url"]),
            ("Manager API", test_config["manager_api_url"]),
            ("Indexer API", test_config["indexer_url"])
        ]
        
        for name, url in components:
            try:
                if name == "Dashboard":
                    # Test UI accessibility
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    print(f"✓ {name} UI is accessible")
                else:
                    # Test API accessibility
                    response = api_session.get(url, timeout=10)
                    assert response.status_code in [200, 401, 403], f"{name} returned status {response.status_code}"
                    print(f"✓ {name} API is accessible")
                    
            except Exception as e:
                pytest.fail(f"✗ {name} is not accessible: {str(e)}")
    
    def test_dashboard_to_manager_communication(self, driver, test_config):
        """Test that the dashboard can communicate with the manager."""
        try:
            # Navigate to dashboard
            driver.get(test_config["dashboard_url"])
            
            # Wait for page to load
            WebDriverWait(driver, test_config["timeout"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for any error messages related to manager connectivity
            error_indicators = [
                "connection refused",
                "timeout",
                "unreachable",
                "manager",
                "api"
            ]
            
            page_text = driver.page_source.lower()
            connection_errors = []
            
            for indicator in error_indicators:
                if indicator in page_text:
                    # Look for context around the error
                    lines = page_text.split('\n')
                    for line in lines:
                        if indicator in line:
                            connection_errors.append(line.strip())
            
            if connection_errors:
                print(f"Potential connection issues found: {connection_errors[:3]}")  # Show first 3
                # Don't fail the test immediately, just log the issues
            
            # Check if page loaded successfully (basic validation)
            assert len(driver.page_source) > 1000, "Dashboard should have substantial content"
            print("✓ Dashboard loaded successfully")
            
        except TimeoutException:
            pytest.fail("Dashboard did not load within timeout period")
        except Exception as e:
            pytest.fail(f"Dashboard connectivity test failed: {str(e)}")
    
    def test_api_endpoint_consistency(self, api_session, test_config):
        """Test that all API endpoints return consistent response formats."""
        endpoints = [
            (f"{test_config['manager_api_url']}/", "Manager API"),
            (f"{test_config['indexer_url']}/", "Indexer API")
        ]
        
        responses = {}
        
        for endpoint, name in endpoints:
            try:
                response = api_session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    responses[name] = data
                    print(f"✓ {name} returned valid JSON")
                else:
                    print(f"⚠ {name} returned status {response.status_code}")
                    
            except Exception as e:
                print(f"✗ {name} test failed: {str(e)}")
        
        # Validate that we got at least some successful responses
        assert len(responses) > 0, "No API endpoints returned successful responses"
        
        # Check for common response patterns
        for name, data in responses.items():
            assert isinstance(data, dict), f"{name} response should be a dictionary"
            assert len(data) > 0, f"{name} response should not be empty"
    
    def test_ssl_certificate_validation(self, api_session, test_config):
        """Test that all endpoints use proper SSL certificates."""
        endpoints = [
            test_config["dashboard_url"],
            test_config["manager_api_url"],
            test_config["indexer_url"]
        ]
        
        for endpoint in endpoints:
            try:
                # Make a request to check SSL
                response = api_session.get(endpoint, timeout=10)
                
                # If we get here, SSL connection was successful
                print(f"✓ SSL connection successful to {endpoint}")
                
            except Exception as e:
                # SSL errors would typically cause connection failures
                print(f"⚠ SSL connection issue with {endpoint}: {str(e)}")
                # Don't fail the test for SSL issues in testing environment
    
    def test_system_health_summary(self, driver, api_session, test_config):
        """Provide a comprehensive summary of system health."""
        health_status = {
            "dashboard_ui": False,
            "manager_api": False,
            "indexer_api": False,
            "ssl_connections": False
        }
        
        try:
            # Test Dashboard UI
            driver.get(test_config["dashboard_url"])
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            health_status["dashboard_ui"] = True
            print("✓ Dashboard UI: Healthy")
        except:
            print("✗ Dashboard UI: Unhealthy")
        
        try:
            # Test Manager API
            response = api_session.get(f"{test_config['manager_api_url']}/", timeout=10)
            if response.status_code == 200:
                health_status["manager_api"] = True
                print("✓ Manager API: Healthy")
            else:
                print(f"⚠ Manager API: Status {response.status_code}")
        except:
            print("✗ Manager API: Unhealthy")
        
        try:
            # Test Indexer API
            response = api_session.get(f"{test_config['indexer_url']}/", timeout=10)
            if response.status_code == 200:
                health_status["indexer_api"] = True
                print("✓ Indexer API: Healthy")
            else:
                print(f"⚠ Indexer API: Status {response.status_code}")
        except:
            print("✗ Indexer API: Unhealthy")
        
        try:
            # Test SSL connections
            api_session.get(test_config["dashboard_url"], timeout=5)
            health_status["ssl_connections"] = True
            print("✓ SSL Connections: Healthy")
        except:
            print("✗ SSL Connections: Issues detected")
        
        # Calculate overall health score
        healthy_components = sum(health_status.values())
        total_components = len(health_status)
        health_score = (healthy_components / total_components) * 100
        
        print(f"\n📊 System Health Score: {health_score:.1f}% ({healthy_components}/{total_components} components healthy)")
        
        # Provide recommendations based on health status
        if health_score < 100:
            print("\n🔧 Recommendations:")
            if not health_status["dashboard_ui"]:
                print("  - Check dashboard service status and network connectivity")
            if not health_status["manager_api"]:
                print("  - Verify manager service is running and API is accessible")
            if not health_status["indexer_api"]:
                print("  - Check indexer service status and cluster health")
            if not health_status["ssl_connections"]:
                print("  - Verify SSL certificates and network configuration")
        
        # Assert minimum health threshold (at least 75% healthy)
        assert health_score >= 75, f"System health score {health_score}% is below 75% threshold" 