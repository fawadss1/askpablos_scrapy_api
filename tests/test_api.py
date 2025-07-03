"""
Test file to validate the enhanced AskPablos API configuration.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from askpablos_scrapy_api.operations import AskPablosAPIMapValidator, create_api_payload


def test_basic_configuration():
    """Test basic configuration validation."""
    config = {
        "browser": True,
        "rotate_proxy": True
    }

    try:
        validated = AskPablosAPIMapValidator.validate_config(config)
        print("✓ Basic configuration validation passed")
        print(f"  Validated config: {validated}")
        return True
    except Exception as e:
        print(f"✗ Basic configuration validation failed: {e}")
        return False


def test_js_strategy_configuration():
    """Test JavaScript strategy configuration validation."""
    configs = [
        {"browser": True, "js_strategy": True},      # Stealth mode
        {"browser": True, "js_strategy": False},     # No JS
        {"browser": True, "js_strategy": "DEFAULT"}  # Default mode
    ]

    for i, config in enumerate(configs):
        try:
            validated = AskPablosAPIMapValidator.validate_config(config)
            print(f"✓ JS strategy test {i+1} passed: {validated['js_strategy']}")
        except Exception as e:
            print(f"✗ JS strategy test {i+1} failed: {e}")
            return False

    return True


def test_advanced_configuration():
    """Test advanced configuration with all options."""
    config = {
        "browser": True,
        "rotate_proxy": True,
        "wait_for_load": True,
        "screenshot": True,
        "js_strategy": "DEFAULT"
    }

    try:
        validated = AskPablosAPIMapValidator.validate_config(config)
        print("✓ Advanced configuration validation passed")
        print(f"  All features validated successfully")
        return True
    except Exception as e:
        print(f"✗ Advanced configuration validation failed: {e}")
        return False


def test_api_payload_creation():
    """Test API payload creation."""
    config = {
        "browser": True,
        "rotate_proxy": True,
        "js_strategy": True
    }

    try:
        validated = AskPablosAPIMapValidator.validate_config(config)
        payload = create_api_payload(
            request_url="https://example.com",
            request_method="GET",
            config=validated
        )

        print("✓ API payload creation passed")
        print(f"  Payload keys: {list(payload.keys())}")
        print(f"  URL: {payload['url']}")
        print(f"  Method: {payload['method']}")
        print(f"  Browser: {payload['browser']}")
        print(f"  Rotate Proxy: {payload['rotateProxy']}")
        print(f"  JS Strategy: {payload['jsStrategy']}")
        return True
    except Exception as e:
        print(f"✗ API payload creation failed: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid configurations."""
    invalid_configs = [
        # Invalid browser type
        {"browser": "yes"},
        # Invalid JS strategy
        {"js_strategy": "INVALID"},
        # Invalid JS strategy type
        {"js_strategy": 123},
    ]

    passed = 0
    for i, config in enumerate(invalid_configs):
        try:
            AskPablosAPIMapValidator.validate_config(config)
            print(f"✗ Error handling test {i+1} failed: Should have raised ValueError")
        except ValueError:
            print(f"✓ Error handling test {i+1} passed: Correctly caught invalid config")
            passed += 1
        except Exception as e:
            print(f"✗ Error handling test {i+1} failed: Unexpected error: {e}")

    return passed == len(invalid_configs)


def main():
    """Run all tests."""
    print("Testing Enhanced AskPablos API Configuration")
    print("=" * 50)

    tests = [
        test_basic_configuration,
        test_js_strategy_configuration,
        test_advanced_configuration,
        test_api_payload_creation,
        test_error_handling
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1
        print("-" * 30)

    print(f"\nTest Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The enhanced API is ready to use.")
    else:
        print("❌ Some tests failed. Please check the implementation.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
