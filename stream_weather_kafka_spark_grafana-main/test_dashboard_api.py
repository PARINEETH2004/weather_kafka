#!/usr/bin/env python3
"""
Test script for the dashboard API
"""
import requests
import time

def test_api():
    base_url = "http://localhost:5000"
    
    print("Testing Dashboard API...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/api/weather")
        print(f"Weather endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Weather API is accessible")
        else:
            print("✗ Weather API returned error")
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API. Make sure weather_api.py is running.")
        return
    
    # Test cities endpoint
    try:
        response = requests.get(f"{base_url}/api/cities")
        print(f"Cities endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Cities API is accessible")
        else:
            print("✗ Cities API returned error")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing cities API: {e}")
    
    # Test alerts endpoint
    try:
        response = requests.get(f"{base_url}/api/alerts")
        print(f"Alerts endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Alerts API is accessible")
        else:
            print("✗ Alerts API returned error")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing alerts API: {e}")
    
    # Test adding a city
    try:
        response = requests.post(
            f"{base_url}/api/monitor/city",
            json={"city": "Test City"}
        )
        print(f"Add city endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Add city API is working")
        else:
            print("✗ Add city API returned error")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error testing add city API: {e}")
    
    print("\nAPI Test Complete!")

if __name__ == "__main__":
    test_api()