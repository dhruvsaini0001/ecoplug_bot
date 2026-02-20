"""
Test Script for EV Charging Diagnostic Chatbot
Tests various scenarios including error detection, flow navigation, and AI fallback.
"""
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000/v1"


def print_test_header(test_name: str):
    """Print test header."""
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)


def print_response(response: Dict[str, Any]):
    """Pretty print response."""
    print("\nResponse:")
    print(json.dumps(response, indent=2))


def test_health_check():
    """Test health check endpoint."""
    print_test_header("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print_response(response.json())
        
        if response.status_code == 200:
            print("✓ PASS")
        else:
            print("✗ FAIL")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_error_code_detection():
    """Test error code detection with ER001."""
    print_test_header("Error Code Detection (ER001)")
    
    payload = {
        "user_id": "test_user_1",
        "message": "I'm getting ER001 error on my charging station",
        "platform": "web"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") == "diagnostic" and data.get("error_code") == "ER001":
            print("✓ PASS - Error code detected correctly")
        else:
            print("✗ FAIL - Expected diagnostic response with ER001")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_fuzzy_error_matching():
    """Test fuzzy matching with natural language."""
    print_test_header("Fuzzy Error Matching (Gun Temperature)")
    
    payload = {
        "user_id": "test_user_2",
        "message": "gun temperature is too high",
        "platform": "android"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") == "diagnostic":
            print("✓ PASS - Fuzzy matching worked")
        else:
            print("⚠ INFO - May fallback to AI (acceptable)")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_error_code_lowercase():
    """Test lowercase error code detection."""
    print_test_header("Lowercase Error Code (er015)")
    
    payload = {
        "user_id": "test_user_3",
        "message": "showing er015",
        "platform": "ios"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") == "diagnostic" and data.get("error_code") == "ER015":
            print("✓ PASS - Lowercase detection works")
        else:
            print("✗ FAIL - Expected ER015 detection")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_numeric_error_code():
    """Test numeric error code with context."""
    print_test_header("Numeric Error Code (error 301)")
    
    payload = {
        "user_id": "test_user_4",
        "message": "I'm seeing error 301 on the display",
        "platform": "web"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") == "diagnostic":
            print("✓ PASS - Numeric code detected")
        else:
            print("⚠ INFO - May need ER301 in database")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_flow_action():
    """Test explicit action routing."""
    print_test_header("Flow Action (start)")
    
    payload = {
        "user_id": "test_user_5",
        "action": "start",
        "platform": "web"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") == "flow":
            print("✓ PASS - Flow routing works")
        else:
            print("✗ FAIL - Expected flow response")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_intent_detection():
    """Test intent-based routing."""
    print_test_header("Intent Detection (help)")
    
    payload = {
        "user_id": "test_user_6",
        "message": "I need help with my charging station",
        "platform": "android"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") in ["flow", "ai"]:
            print("✓ PASS - Intent detected or AI fallback")
        else:
            print("✗ FAIL - Expected flow or AI response")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_ai_fallback():
    """Test AI fallback for unknown queries."""
    print_test_header("AI Fallback (general query)")
    
    payload = {
        "user_id": "test_user_7",
        "message": "What is the meaning of life?",
        "platform": "ios"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        print_response(data)
        
        if data.get("type") == "ai":
            print("✓ PASS - AI fallback engaged")
        else:
            print("⚠ INFO - Unexpected routing")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def test_session_continuity():
    """Test session management."""
    print_test_header("Session Continuity")
    
    user_id = "test_user_session"
    
    # First request
    payload1 = {
        "user_id": user_id,
        "action": "start",
        "platform": "web"
    }
    
    try:
        response1 = requests.post(f"{BASE_URL}/chat", json=payload1)
        data1 = response1.json()
        session_id_1 = data1.get("session_id")
        print(f"First request session: {session_id_1}")
        
        # Second request (should reuse session)
        payload2 = {
            "user_id": user_id,
            "message": "help",
            "platform": "web"
        }
        
        response2 = requests.post(f"{BASE_URL}/chat", json=payload2)
        data2 = response2.json()
        session_id_2 = data2.get("session_id")
        print(f"Second request session: {session_id_2}")
        
        if session_id_1 == session_id_2:
            print("✓ PASS - Session persisted")
        else:
            print("✗ FAIL - Session not maintained")
    except Exception as e:
        print(f"✗ ERROR: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 EV CHARGING CHATBOT - API TESTS")
    print("=" * 60)
    print(f"\nTarget: {BASE_URL}")
    print("\nMake sure the server is running: python run.py")
    input("\nPress Enter to start tests...")
    
    # Run tests
    test_health_check()
    test_error_code_detection()
    test_fuzzy_error_matching()
    test_error_code_lowercase()
    test_numeric_error_code()
    test_flow_action()
    test_intent_detection()
    test_ai_fallback()
    test_session_continuity()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
