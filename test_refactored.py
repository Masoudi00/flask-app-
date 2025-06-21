#!/usr/bin/env python3
"""
Simple test script to verify the refactored application structure
"""

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        # Test configuration imports
        from config.database import init_database, init_session
        print("✓ Configuration imports successful")
        
        # Test model imports
        from models.user import User
        from models.portfolio import Portfolio
        from models.watchlist import Watchlist, PriceAlert
        print("✓ Model imports successful")
        
        # Test route imports
        from routes.auth import init_auth_routes
        from routes.portfolio import init_portfolio_routes
        from routes.quote import init_quote_routes
        from routes.features import init_features_routes
        print("✓ Route imports successful")
        
        # Test utility imports
        from utils.helpers import apology, login_required, usd
        from utils.stock_utils import lookup, get_stock_sector, get_popular_stocks
        print("✓ Utility imports successful")
        
        # Test main app import
        from app import create_app
        print("✓ Main app import successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created"""
    try:
        from app import create_app
        from flask import Flask
        
        app = create_app()
        
        if isinstance(app, Flask):
            print("✓ Flask app creation successful")
            return True
        else:
            print("✗ App creation failed - not a Flask instance")
            return False
            
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_utility_functions():
    """Test basic utility functions"""
    try:
        from utils.helpers import usd
        from utils.stock_utils import get_popular_stocks
        
        # Test USD formatting
        formatted = usd(1234.56)
        if formatted == "$1,234.56":
            print("✓ USD formatting works correctly")
        else:
            print(f"✗ USD formatting failed: expected $1,234.56, got {formatted}")
            return False
        
        # Test popular stocks
        stocks = get_popular_stocks()
        if len(stocks) > 0 and "AAPL" in stocks:
            print("✓ Popular stocks function works correctly")
        else:
            print("✗ Popular stocks function failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Utility function test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing refactored Finance application...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("App Creation Test", test_app_creation),
        ("Utility Function Tests", test_utility_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The refactored application is ready to use.")
        print("\nTo run the application:")
        print("  python app_new.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 