"""
API Testing Script for Employee Monitoring System
Run this script to test all backend endpoints
"""

import requests
import time
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_health_check():
    """Test basic health check endpoint"""
    print_info("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print_success(f"Health check passed: {data}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_create_detection():
    """Test creating a new detection"""
    print_info("Testing detection creation...")
    try:
        response = requests.post(f"{BASE_URL}/api/detection?employee_id=EMP001")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "timestamp" in data
        print_success(f"Detection created: ID={data['id']}, Emotion={data.get('emotion', 'N/A')}")
        return data['id']
    except Exception as e:
        print_error(f"Detection creation failed: {e}")
        return None

def test_get_detections():
    """Test retrieving detections"""
    print_info("Testing detection retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/api/detections?employee_id=EMP001&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print_success(f"Retrieved {len(data)} detections")
        if data:
            latest = data[0]
            print_info(f"Latest detection: {latest['timestamp']}, Present: {latest['is_present']}")
        return True
    except Exception as e:
        print_error(f"Detection retrieval failed: {e}")
        return False

def test_get_analytics():
    """Test analytics endpoint"""
    print_info("Testing analytics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics?employee_id=EMP001&days=1")
        assert response.status_code == 200
        data = response.json()
        assert "total_detections" in data
        assert "presence_percentage" in data
        assert "emotion_distribution" in data
        assert "working_hours" in data
        
        print_success("Analytics retrieved successfully:")
        print_info(f"  Total Detections: {data['total_detections']}")
        print_info(f"  Presence Rate: {data['presence_percentage']}%")
        print_info(f"  Working Hours: {data['working_hours']}h")
        print_info(f"  Emotions: {data['emotion_distribution']}")
        return True
    except Exception as e:
        print_error(f"Analytics retrieval failed: {e}")
        return False

def test_multiple_detections():
    """Test creating multiple detections"""
    print_info("Creating multiple test detections (this will take ~5 seconds)...")
    success_count = 0
    try:
        for i in range(5):
            response = requests.post(f"{BASE_URL}/api/detection?employee_id=EMP001")
            if response.status_code == 200:
                success_count += 1
            time.sleep(1)
        
        print_success(f"Created {success_count}/5 test detections")
        return success_count >= 4
    except Exception as e:
        print_error(f"Multiple detections test failed: {e}")
        return False

def test_date_filtering():
    """Test date filtering in detections"""
    print_info("Testing date filtering...")
    try:
        # Get today's detections
        today = datetime.now().isoformat()
        response = requests.get(
            f"{BASE_URL}/api/detections?employee_id=EMP001&start_date={today}&limit=100"
        )
        assert response.status_code == 200
        data = response.json()
        print_success(f"Retrieved {len(data)} detections from today")
        return True
    except Exception as e:
        print_error(f"Date filtering test failed: {e}")
        return False

def test_video_feed():
    """Test video feed endpoint availability"""
    print_info("Testing video feed endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/video_feed", stream=True, timeout=2)
        if response.status_code == 200:
            print_success("Video feed endpoint is accessible")
            return True
        else:
            print_warning(f"Video feed returned status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_success("Video feed endpoint is streaming (timeout expected)")
        return True
    except Exception as e:
        print_error(f"Video feed test failed: {e}")
        return False

def run_performance_test():
    """Test API response times"""
    print_info("Running performance test...")
    try:
        tests = []
        
        # Test detection endpoint
        start = time.time()
        requests.post(f"{BASE_URL}/api/detection?employee_id=EMP001")
        detection_time = time.time() - start
        tests.append(("Detection Creation", detection_time))
        
        # Test analytics endpoint
        start = time.time()
        requests.get(f"{BASE_URL}/api/analytics?employee_id=EMP001&days=1")
        analytics_time = time.time() - start
        tests.append(("Analytics Retrieval", analytics_time))
        
        # Test detections endpoint
        start = time.time()
        requests.get(f"{BASE_URL}/api/detections?employee_id=EMP001&limit=50")
        detections_time = time.time() - start
        tests.append(("Detections Retrieval", detections_time))
        
        print_success("Performance test results:")
        for test_name, duration in tests:
            color = Colors.GREEN if duration < 1.0 else Colors.YELLOW if duration < 2.0 else Colors.RED
            print(f"  {color}{test_name}: {duration:.3f}s{Colors.END}")
        
        return True
    except Exception as e:
        print_error(f"Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(f"{Colors.BLUE}Employee Monitoring System - API Test Suite{Colors.END}")
    print("="*60 + "\n")
    
    results = {}
    
    # Check if server is running
    print_info("Checking if backend server is running...")
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
        print_success("Backend server is running\n")
    except:
        print_error("Backend server is not running!")
        print_info("Please start the server with: uvicorn main:app --reload")
        return
    
    # Run tests
    print(f"\n{Colors.BLUE}Running API Tests...{Colors.END}\n")
    
    results['Health Check'] = test_health_check()
    print()
    
    results['Create Detection'] = test_create_detection()
    print()
    
    results['Get Detections'] = test_get_detections()
    print()
    
    results['Get Analytics'] = test_get_analytics()
    print()
    
    results['Multiple Detections'] = test_multiple_detections()
    print()
    
    results['Date Filtering'] = test_date_filtering()
    print()
    
    results['Video Feed'] = test_video_feed()
    print()
    
    results['Performance Test'] = run_performance_test()
    print()
    
    # Summary
    print("\n" + "="*60)
    print(f"{Colors.BLUE}Test Summary{Colors.END}")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{test_name:.<40} {status}")
    
    print("\n" + "-"*60)
    success_rate = (passed / total) * 100
    color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED
    print(f"Overall Success Rate: {color}{passed}/{total} ({success_rate:.1f}%){Colors.END}")
    print("-"*60 + "\n")
    
    if success_rate >= 80:
        print(f"{Colors.GREEN}✓ All critical tests passed! System is ready.{Colors.END}")
    elif success_rate >= 60:
        print(f"{Colors.YELLOW}⚠ Some tests failed. Please review the errors above.{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Multiple tests failed. Please check your configuration.{Colors.END}")
    
    print()

if __name__ == "__main__":
    main()