import asyncio

import aiohttp

from config import OPENWEATHERMAP_API_KEY


async def get_weather_data(city, api_key: str = OPENWEATHERMAP_API_KEY) -> dict:
    URL = f'https://api.openweathermap.org/data/2.5/weather'
    # ?q={city name}&appid={API key}

    params = {
        'appid': api_key,
        'q': city,
        'units': 'metric',
        'lang': 'ru'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, params=params) as response:
            if response.status == 200:
                response_dict = await response.json()
                weather_description = response_dict['weather'][0]['description']
                current_temp = response_dict['main']['temp']
                result = {
                    'description': weather_description,
                    'temperature': current_temp
                }

                return result
            return {}
