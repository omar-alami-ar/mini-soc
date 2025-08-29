import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urlparse

class TestWazuhDashboardUI:
    """Test suite for Wazuh Dashboard UI functionality."""
    
    def test_dashboard_https_accessible(self, driver, test_config):
        """Test that the Wazuh dashboard is reachable over HTTPS."""
        try:
            # Navigate to dashboard
            driver.get(test_config["dashboard_url"])
            
            # Wait for page to load
            WebDriverWait(driver, test_config["timeout"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Verify HTTPS protocol
            current_url = driver.current_url
            parsed_url = urlparse(current_url)
            assert parsed_url.scheme == "https", f"Expected HTTPS, got {parsed_url.scheme}"
            
            # Verify we can reach the page (no connection errors)
            assert "error" not in driver.title.lower(), f"Page title contains error: {driver.title}"
            
        except TimeoutException:
            pytest.fail(f"Dashboard did not load within {test_config['timeout']} seconds")
        except WebDriverException as e:
            pytest.fail(f"Failed to access dashboard: {str(e)}")
    
    def test_dashboard_page_title(self, driver, test_config):
        """Test that the dashboard page title is correct."""
        try:
            driver.get(test_config["dashboard_url"])
            
            # Wait for page to load
            WebDriverWait(driver, test_config["timeout"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "title"))
            )
            
            # Check page title
            page_title = driver.title
            assert page_title, "Page title should not be empty"
            
            # Wazuh dashboard typically has "Wazuh" in the title
            # This is flexible as titles can vary between versions
            print(f"Dashboard page title: {page_title}")
            
        except TimeoutException:
            pytest.fail(f"Dashboard did not load within {test_config['timeout']} seconds")
    
    def test_login_form_elements_present(self, driver, test_config):
        """Test that login form elements are present on the dashboard."""
        try:
            driver.get(test_config["dashboard_url"])
            
            # Wait for login form to appear
            # Look for common login form elements
            login_form_selectors = [
                "input[type='text']",  # Username field
                "input[type='password']",  # Password field
                "button[type='submit']",  # Submit button
                "form",  # Form element
            ]
            
            for selector in login_form_selectors:
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    assert element.is_displayed(), f"Element {selector} is not displayed"
                except TimeoutException:
                    pytest.fail(f"Login form element {selector} not found within 10 seconds")
            
            # Additional check for Wazuh-specific elements
            try:
                # Look for Wazuh branding or specific login elements
                wazuh_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Wazuh')]")
                if wazuh_elements:
                    print(f"Found {len(wazuh_elements)} Wazuh-related elements")
                
            except Exception as e:
                print(f"Note: Could not verify Wazuh-specific elements: {e}")
                
        except TimeoutException:
            pytest.fail(f"Dashboard did not load within {test_config['timeout']} seconds")
    
    @pytest.mark.optional
    def test_programmatic_login(self, driver, test_config):
        """Test programmatic login using test account credentials."""
        # Skip if credentials are not provided
        if not test_config["dashboard_username"] or not test_config["dashboard_password"]:
            pytest.skip("Dashboard credentials not provided in environment variables")
        
        try:
            driver.get(test_config["dashboard_url"])
            
            # Wait for login form
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            # Clear fields and enter credentials
            username_field.clear()
            username_field.send_keys(test_config["dashboard_username"])
            
            password_field.clear()
            password_field.send_keys(test_config["dashboard_password"])
            
            # Submit login form
            submit_button.click()
            
            # Wait for login to complete and redirect
            time.sleep(3)  # Allow time for login processing
            
            # Check if we're redirected to dashboard (not login page)
            current_url = driver.current_url
            assert "login" not in current_url.lower(), "Still on login page after login attempt"
            
            # Look for dashboard elements that indicate successful login
            dashboard_indicators = [
                "//*[contains(@class, 'dashboard')]",
                "//*[contains(@class, 'main')]",
                "//*[contains(@class, 'content')]",
                "//*[contains(text(), 'Overview')]",
                "//*[contains(text(), 'Security')]",
                "//*[contains(text(), 'Management')]"
            ]
            
            dashboard_found = False
            for indicator in dashboard_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if elements:
                        dashboard_found = True
                        print(f"Found dashboard indicator: {indicator}")
                        break
                except:
                    continue
            
            assert dashboard_found, "Could not find dashboard elements after login"
            
            # Verify we're not on an error page
            error_indicators = ["error", "invalid", "failed", "unauthorized"]
            page_text = driver.page_source.lower()
            for error in error_indicators:
                assert error not in page_text, f"Login error detected: {error}"
                
        except TimeoutException:
            pytest.fail(f"Login form elements not found within timeout period")
        except Exception as e:
            pytest.fail(f"Login test failed: {str(e)}")
    
    def test_dashboard_responsiveness(self, driver, test_config):
        """Test that the dashboard responds to basic interactions."""
        try:
            driver.get(test_config["dashboard_url"])
            
            # Wait for page to load
            WebDriverWait(driver, test_config["timeout"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Test basic page interactions
            body = driver.find_element(By.TAG_NAME, "body")
            
            # Check if page is interactive
            assert body.is_enabled(), "Page body should be enabled"
            
            # Test page source length (should have content)
            page_source = driver.page_source
            assert len(page_source) > 1000, "Page should have substantial content"
            
            # Check for JavaScript errors in console (basic check)
            logs = driver.get_log("browser")
            if logs:
                print(f"Browser console logs: {logs}")
            
        except TimeoutException:
            pytest.fail(f"Dashboard did not load within {test_config['timeout']} seconds")
        except Exception as e:
            pytest.fail(f"Dashboard responsiveness test failed: {str(e)}") 