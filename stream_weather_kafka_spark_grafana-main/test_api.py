import requests
import json

def test_weather_api():
    api_key = "b8bfddab1e0d47c54a08d4dd861d44b6"
    # Test with a fixed location (New York)
    url = f"http://api.openweathermap.org/data/2.5/weather?q=New York&appid={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("API is working correctly!")
        print(f"City: {data['name']}")
        print(f"Temperature: {data['main']['temp']}K")
        print(f"Description: {data['weather'][0]['description']}")
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_weather_api()