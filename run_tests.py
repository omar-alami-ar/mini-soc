#!/usr/bin/env python3
"""
Wazuh SOC Testing Suite Runner

This script provides an easy way to run different types of tests for the Wazuh deployment.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Command completed successfully")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import selenium
        import pytest
        import requests
        print("✅ All Python dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements-test.txt")
        return False

def setup_environment():
    """Set up the testing environment."""
    print("🔧 Setting up testing environment...")
    
    # Create test results directory
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)
    print(f"✅ Test results directory: {results_dir}")
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Please copy env.example to .env and configure your settings.")
        print("   Tests may fail without proper configuration.")
    else:
        print("✅ Environment configuration file found")
    
    return True

def run_ui_tests():
    """Run UI tests only."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_dashboard_ui.py",
        "-v",
        "--tb=short",
        "--html=test-results/ui-report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Running UI Tests")

def run_api_tests():
    """Run API tests only."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_api_health.py",
        "-v",
        "--tb=short",
        "--html=test-results/api-report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Running API Tests")

def run_integration_tests():
    """Run integration tests only."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_integration.py",
        "-v",
        "--tb=short",
        "--html=test-results/integration-report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Running Integration Tests")

def run_all_tests():
    """Run all tests."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/",
        "-v",
        "--tb=short",
        "--html=test-results/full-report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Running All Tests")

def run_quick_tests():
    """Run quick tests (skip optional and slow tests)."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/",
        "-v",
        "--tb=short",
        "-m", "not optional and not slow",
        "--html=test-results/quick-report.html",
        "--self-contained-html"
    ]
    return run_command(cmd, "Running Quick Tests (excluding optional and slow tests)")

def run_health_check():
    """Run a basic health check."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_integration.py::TestWazuhIntegration::test_system_health_summary",
        "-v",
        "--tb=short"
    ]
    return run_command(cmd, "Running System Health Check")

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Wazuh SOC Testing Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --ui                     # Run UI tests only
  python run_tests.py --api                    # Run API tests only
  python run_tests.py --integration            # Run integration tests only
  python run_tests.py --quick                  # Run quick tests (skip optional/slow)
  python run_tests.py --health                 # Run health check only
  python run_tests.py --install-deps           # Install dependencies
        """
    )
    
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--quick", action="store_true", help="Run quick tests (skip optional/slow)")
    parser.add_argument("--health", action="store_true", help="Run health check only")
    parser.add_argument("--install-deps", action="store_true", help="Install Python dependencies")
    
    args = parser.parse_args()
    
    print("🔒 Wazuh SOC Testing Suite")
    print("=" * 50)
    
    # Install dependencies if requested
    if args.install_deps:
        print("📦 Installing dependencies...")
        cmd = ["pip", "install", "-r", "requirements-test.txt"]
        if run_command(cmd, "Installing Dependencies"):
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies")
            sys.exit(1)
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first:")
        print("   python run_tests.py --install-deps")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Failed to setup testing environment")
        sys.exit(1)
    
    # Run tests based on arguments
    success = True
    
    if args.ui:
        success &= run_ui_tests()
    elif args.api:
        success &= run_api_tests()
    elif args.integration:
        success &= run_integration_tests()
    elif args.quick:
        success &= run_quick_tests()
    elif args.health:
        success &= run_health_check()
    elif args.all:
        success &= run_all_tests()
    else:
        # Default: run health check
        print("ℹ️  No specific test type specified, running health check...")
        success &= run_health_check()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All requested tests completed successfully!")
        print("📊 Check test-results/ directory for detailed reports")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 