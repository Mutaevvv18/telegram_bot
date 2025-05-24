import requests
from config import OPENWEATHER_API_KEY


def get_weather(city: str) -> dict:
    base_url = "https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}"

    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()

    return {
        'temp': data['main']['temp'],
        'feels_like': data['main']['feels_like'],
        'humidity': data['main']['humidity'],
        'pressure': data['main']['pressure'] * 0.750062,  # переводим в мм рт.ст.
        'wind_speed': data['wind']['speed'],
        'description': data['weather'][0]['description']
    }