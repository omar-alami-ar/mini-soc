#!/usr/bin/env python3
"""
Wazuh SOC Health Check Script

A lightweight script to quickly check the health of Wazuh components.
"""

import os
import sys
import requests
import time
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_endpoint(url, name, timeout=10):
    """Check if an endpoint is accessible."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout, verify=False)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            return True, response_time, response.status_code, None
        else:
            return False, response_time, response.status_code, f"HTTP {response.status_code}"
            
    except requests.exceptions.SSLError as e:
        return False, 0, 0, f"SSL Error: {str(e)}"
    except requests.exceptions.ConnectionError as e:
        return False, 0, 0, f"Connection Error: {str(e)}"
    except requests.exceptions.Timeout as e:
        return False, 0, 0, f"Timeout: {str(e)}"
    except Exception as e:
        return False, 0, 0, f"Error: {str(e)}"

def check_ui_accessibility(url, timeout=10):
    """Check if the UI is accessible."""
    try:
        response = requests.get(url, timeout=timeout, verify=False)
        if response.status_code == 200:
            return True, response.status_code, None
        else:
            return False, response.status_code, f"HTTP {response.status_code}"
    except Exception as e:
        return False, 0, str(e)

def main():
    """Main health check function."""
    print("🔒 Wazuh SOC Health Check")
    print("=" * 50)
    
    # Configuration
    config = {
        "dashboard_url": os.getenv("WAZUH_DASHBOARD_URL", "https://localhost:443"),
        "manager_api_url": os.getenv("WAZUH_MANAGER_API_URL", "https://localhost:55000"),
        "indexer_url": os.getenv("WAZUH_INDEXER_URL", "https://localhost:9200"),
    }
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  No .env file found. Using default localhost URLs.")
        print("   Create .env file from env.example for production URLs.\n")
    
    # Health status tracking
    health_status = {
        "dashboard_ui": False,
        "manager_api": False,
        "indexer_api": False,
        "ssl_validation": False
    }
    
    # Test Dashboard UI
    print("🔍 Checking Dashboard UI...")
    accessible, status_code, error = check_ui_accessibility(config["dashboard_url"])
    if accessible:
        print(f"✅ Dashboard UI: Accessible (HTTP {status_code})")
        health_status["dashboard_ui"] = True
    else:
        print(f"❌ Dashboard UI: Not accessible - {error}")
    
    # Test Manager API
    print("\n🔍 Checking Manager API...")
    accessible, response_time, status_code, error = check_endpoint(config["manager_api_url"], "Manager API")
    if accessible:
        print(f"✅ Manager API: Healthy (HTTP {status_code}, {response_time:.2f}s)")
        health_status["manager_api"] = True
    else:
        print(f"❌ Manager API: Unhealthy - {error}")
    
    # Test Indexer API
    print("\n🔍 Checking Indexer API...")
    accessible, response_time, status_code, error = check_endpoint(config["indexer_url"], "Indexer API")
    if accessible:
        print(f"✅ Indexer API: Healthy (HTTP {status_code}, {response_time:.2f}s)")
        health_status["indexer_api"] = True
    else:
        print(f"❌ Indexer API: Unhealthy - {error}")
    
    # Test SSL Configuration
    print("\n🔍 Checking SSL Configuration...")
    ssl_issues = []
    for name, url in [
        ("Dashboard", config["dashboard_url"]),
        ("Manager API", config["manager_api_url"]),
        ("Indexer API", config["indexer_url"])
    ]:
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            print(f"✅ {name}: HTTPS configured")
        else:
            print(f"❌ {name}: Not using HTTPS")
            ssl_issues.append(name)
    
    if not ssl_issues:
        health_status["ssl_validation"] = True
        print("✅ All endpoints use HTTPS")
    else:
        print(f"⚠️  SSL issues found with: {', '.join(ssl_issues)}")
    
    # Calculate health score
    healthy_components = sum(health_status.values())
    total_components = len(health_status)
    health_score = (healthy_components / total_components) * 100
    
    print("\n" + "=" * 50)
    print(f"📊 System Health Score: {health_score:.1f}% ({healthy_components}/{total_components} components healthy)")
    
    # Health status summary
    print("\n📋 Component Status:")
    for component, status in health_status.items():
        status_icon = "✅" if status else "❌"
        status_text = "Healthy" if status else "Unhealthy"
        print(f"  {status_icon} {component.replace('_', ' ').title()}: {status_text}")
    
    # Recommendations
    if health_score < 100:
        print("\n🔧 Recommendations:")
        if not health_status["dashboard_ui"]:
            print("  - Check dashboard service status and network connectivity")
            print("  - Verify dashboard is running on the expected port")
        if not health_status["manager_api"]:
            print("  - Verify manager service is running")
            print("  - Check manager API configuration and firewall rules")
        if not health_status["indexer_api"]:
            print("  - Check indexer service status")
            print("  - Verify indexer cluster health")
        if not health_status["ssl_validation"]:
            print("  - Ensure all endpoints use HTTPS")
            print("  - Check SSL certificate configuration")
    
    # Final status
    if health_score >= 75:
        print(f"\n🎉 System is healthy! ({health_score:.1f}%)")
        return 0
    elif health_score >= 50:
        print(f"\n⚠️  System has issues but is operational ({health_score:.1f}%)")
        return 1
    else:
        print(f"\n❌ System is unhealthy ({health_score:.1f}%)")
        return 2

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1) 