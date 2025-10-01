#!/usr/bin/env python3
"""
Test setup script for TradeTrack.
Installs test dependencies and verifies the test environment.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"✓ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  ✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {description} failed: {e.stderr}")
        return False


def install_test_dependencies():
    """Install test dependencies."""
    print("🔧 Installing test dependencies...")
    
    # Get the directory containing this script
    test_dir = Path(__file__).parent
    requirements_file = test_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"✗ Test requirements file not found: {requirements_file}")
        return False
    
    # Install test dependencies
    success = run_command(
        f"pip install -r {requirements_file}",
        "Installing test dependencies"
    )
    
    return success


def verify_test_environment():
    """Verify that the test environment is properly set up."""
    print("\n🔍 Verifying test environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"✗ Python version {python_version.major}.{python_version.minor} is below minimum required 3.9")
        return False
    else:
        print(f"✓ Python version {python_version.major}.{python_version.minor} is compatible")
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__} is available")
    except ImportError:
        print("✗ pytest is not available")
        return False
    
    # Check if other test dependencies are available
    test_modules = [
        'pytest_cov',
        'pytest_mock',
        'pytest_xdist',
        'black',
        'flake8',
        'isort',
        'mypy',
        'bandit',
        'safety',
        'psutil'
    ]
    
    missing_modules = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"✓ {module} is available")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} is not available")
    
    if missing_modules:
        print(f"\n⚠️  Missing modules: {', '.join(missing_modules)}")
        print("Run 'pip install -r tests/requirements.txt' to install them")
        return False
    
    return True


def run_basic_tests():
    """Run basic tests to verify everything works."""
    print("\n🧪 Running basic tests...")
    
    # Run syntax tests
    success = run_command(
        "python -m pytest tests/test_syntax.py::TestSyntax::test_python_syntax_validation -v",
        "Running syntax validation test"
    )
    
    if not success:
        return False
    
    # Run a simple unit test
    success = run_command(
        "python -m pytest tests/test_config_loader.py::TestConfigLoader::test_config_loader_init_default -v",
        "Running unit test"
    )
    
    return success


def main():
    """Main setup function."""
    print("🚀 TradeTrack Test Environment Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("ttrack.py").exists():
        print("✗ Please run this script from the TradeTrack root directory")
        sys.exit(1)
    
    # Install test dependencies
    if not install_test_dependencies():
        print("\n❌ Failed to install test dependencies")
        sys.exit(1)
    
    # Verify test environment
    if not verify_test_environment():
        print("\n❌ Test environment verification failed")
        sys.exit(1)
    
    # Run basic tests
    if not run_basic_tests():
        print("\n❌ Basic tests failed")
        sys.exit(1)
    
    print("\n🎉 Test environment setup completed successfully!")
    print("\nYou can now run tests using:")
    print("  python tests/run_tests.py")
    print("  python -m pytest tests/ -v")
    print("  python tests/run_tests.py --unit")
    print("  python tests/run_tests.py --integration")


if __name__ == "__main__":
    main()
