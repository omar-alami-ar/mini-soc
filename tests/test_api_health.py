import pytest
import json
import jsonschema
from jsonschema import validate
import requests

class TestWazuhAPIHealth:
    """Test suite for Wazuh API health endpoints."""
    
    def test_manager_api_health(self, api_session, test_config):
        """Test that the Wazuh manager API endpoint returns 200 and valid JSON."""
        try:
            # Test basic connectivity to manager API
            response = api_session.get(
                f"{test_config['manager_api_url']}/",
                timeout=30
            )
            
            # Check HTTP status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
            
            # Parse JSON response
            try:
                data = response.json()
                assert isinstance(data, dict), "Response should be a JSON object"
                
                # Basic schema validation for manager API response
                expected_schema = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "api_version": {"type": "string"},
                        "revision": {"type": "string"}
                    },
                    "required": ["title"]
                }
                
                # Validate against schema (allow extra fields)
                validate(instance=data, schema=expected_schema)
                
                print(f"Manager API response: {json.dumps(data, indent=2)}")
                
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")
            except jsonschema.exceptions.ValidationError as e:
                pytest.fail(f"Response does not match expected schema: {e}")
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to manager API: {str(e)}")
    
    def test_manager_api_version(self, api_session, test_config):
        """Test that the manager API version endpoint is accessible."""
        try:
            response = api_session.get(
                f"{test_config['manager_api_url']}/version",
                timeout=30
            )
            
            # Check HTTP status (200 or 404 is acceptable for version endpoint)
            assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
                
                # Parse and validate version response
                data = response.json()
                assert isinstance(data, dict), "Version response should be a JSON object"
                
                # Version response typically contains version info
                if 'api_version' in data:
                    print(f"Manager API version: {data['api_version']}")
                elif 'version' in data:
                    print(f"Manager version: {data['version']}")
                    
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to manager API version endpoint: {str(e)}")
    
    def test_indexer_api_health(self, api_session, test_config):
        """Test that the Wazuh indexer (OpenSearch) API endpoint returns 200 and valid JSON."""
        try:
            # Test basic connectivity to indexer API
            response = api_session.get(
                f"{test_config['indexer_url']}/",
                timeout=30
            )
            
            # Check HTTP status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
            
            # Parse JSON response
            try:
                data = response.json()
                assert isinstance(data, dict), "Response should be a JSON object"
                
                # Basic schema validation for OpenSearch response
                expected_schema = {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "cluster_name": {"type": "string"},
                        "version": {"type": "object"},
                        "tagline": {"type": "string"}
                    },
                    "required": ["name", "cluster_name", "version"]
                }
                
                # Validate against schema (allow extra fields)
                validate(instance=data, schema=expected_schema)
                
                print(f"Indexer API response: {json.dumps(data, indent=2)}")
                
                # Check for OpenSearch/Wazuh indexer specific indicators
                if 'tagline' in data:
                    assert 'opensearch' in data['tagline'].lower() or 'elasticsearch' in data['tagline'].lower(), \
                        "Should be OpenSearch or Elasticsearch"
                
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")
            except jsonschema.exceptions.ValidationError as e:
                pytest.fail(f"Response does not match expected schema: {e}")
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to indexer API: {str(e)}")
    
    def test_indexer_cluster_health(self, api_session, test_config):
        """Test that the indexer cluster health endpoint is accessible."""
        try:
            response = api_session.get(
                f"{test_config['indexer_url']}/_cluster/health",
                timeout=30
            )
            
            # Check HTTP status
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
            
            # Parse and validate cluster health response
            data = response.json()
            assert isinstance(data, dict), "Cluster health response should be a JSON object"
            
            # Cluster health schema validation
            health_schema = {
                "type": "object",
                "properties": {
                    "cluster_name": {"type": "string"},
                    "status": {"type": "string", "enum": ["green", "yellow", "red"]},
                    "number_of_nodes": {"type": "integer"},
                    "active_primary_shards": {"type": "integer"},
                    "active_shards": {"type": "integer"}
                },
                "required": ["cluster_name", "status", "number_of_nodes"]
            }
            
            validate(instance=data, schema=health_schema)
            
            # Check cluster status
            status = data.get('status')
            assert status in ['green', 'yellow', 'red'], f"Unexpected cluster status: {status}"
            
            print(f"Cluster health: {data['status']} - {data['number_of_nodes']} nodes")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to indexer cluster health endpoint: {str(e)}")
        except jsonschema.exceptions.ValidationError as e:
            pytest.fail(f"Cluster health response does not match expected schema: {e}")
    
    def test_dashboard_api_health(self, api_session, test_config):
        """Test that the Wazuh dashboard API endpoint is accessible."""
        try:
            # Test basic connectivity to dashboard API
            response = api_session.get(
                f"{test_config['dashboard_url']}/api/status",
                timeout=30
            )
            
            # Dashboard API might return different status codes depending on authentication
            # 200 = authenticated, 401 = unauthenticated, 403 = forbidden
            assert response.status_code in [200, 401, 403], f"Unexpected status code: {response.status_code}"
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
                
                # Parse and validate response
                data = response.json()
                assert isinstance(data, dict), "Dashboard API response should be a JSON object"
                
                print(f"Dashboard API response: {json.dumps(data, indent=2)}")
            else:
                print(f"Dashboard API requires authentication (status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Failed to connect to dashboard API: {str(e)}")
    
    def test_api_ssl_validation(self, api_session, test_config):
        """Test that all API endpoints use HTTPS."""
        endpoints = [
            test_config['manager_api_url'],
            test_config['indexer_url'],
            test_config['dashboard_url']
        ]
        
        for endpoint in endpoints:
            parsed_url = requests.utils.urlparse(endpoint)
            assert parsed_url.scheme == 'https', f"Endpoint {endpoint} should use HTTPS, got {parsed_url.scheme}"
        
        print("All API endpoints are configured to use HTTPS")
    
    def test_api_response_times(self, api_session, test_config):
        """Test that API endpoints respond within acceptable time limits."""
        endpoints = [
            (f"{test_config['manager_api_url']}/", "Manager API"),
            (f"{test_config['indexer_url']}/", "Indexer API"),
            (f"{test_config['dashboard_url']}/", "Dashboard")
        ]
        
        max_response_time = 5.0  # 5 seconds max response time
        
        for endpoint, name in endpoints:
            try:
                start_time = requests.utils.time.time()
                response = api_session.get(endpoint, timeout=30)
                response_time = requests.utils.time.time() - start_time
                
                assert response_time < max_response_time, \
                    f"{name} response time {response_time:.2f}s exceeds {max_response_time}s limit"
                
                print(f"{name} response time: {response_time:.2f}s")
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Failed to test {name} response time: {str(e)}") 