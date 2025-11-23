#!/usr/bin/env python3
"""
Script to start the complete weather streaming system
"""
import subprocess
import sys
import time
import os

def main():
    print("Starting Weather Streaming System...")
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Start the weather API in the background
    print("Starting Weather API...")
    api_process = subprocess.Popen([sys.executable, "weather_api.py"])
    time.sleep(3)  # Give the API time to start
    
    # Start the weather producer in the background
    print("Starting Weather Producer...")
    producer_process = subprocess.Popen([sys.executable, "weather_kafka_producer.py"])
    
    print("\nWeather Streaming System Started!")
    print("Components running:")
    print("- Weather API (http://localhost:5000)")
    print("- Weather Producer (sending data to Kafka)")
    print("\nTo view the dashboard:")
    print("1. Open weather_dashboard.html in your web browser")
    print("2. The dashboard will connect to the API automatically")
    print("\nPress Ctrl+C to stop all components")
    
    try:
        # Wait for processes to complete (they won't unless interrupted)
        api_process.wait()
        producer_process.wait()
    except KeyboardInterrupt:
        print("\n\nStopping all components...")
        api_process.terminate()
        producer_process.terminate()
        print("All components stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()