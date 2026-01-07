import asyncio
import re
from typing import List

import aiohttp
from aiogram import Dispatcher

from config import FATSECRET_CLIENT_ID, FATSECRET_CLIENT_SECRET


class Food:
    DESCRIPTION_PATTERN = re.compile(
        r'Per\s+(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>\w{1,3})\s*-\s*'
        r'Calories:\s*(?P<calories>\d+(?:\.\d+)?)\s*kcal\s*\|\s*'
        r'Fat:\s*(?P<fat>\d+(?:\.\d+)?)\s*g\s*\|\s*'
        r'Carbs:\s*(?P<carbs>\d+(?:\.\d+)?)\s*g\s*\|\s*'
        r'Protein:\s*(?P<protein>\d+(?:\.\d+)?)\s*g',
        flags=re.IGNORECASE
    )

    def __init__(self, food_name: str, description: str) -> None:
        self.name = food_name
        self.description = description
        self.parse_description()

    def parse_description(self) -> None:
        match_desciption = Food.DESCRIPTION_PATTERN.match(self.description)
        data = match_desciption.groupdict() if match_desciption is not None else {}

        self.amount = float(data['amount']) if data.get('amount') else None
        self.unit = data['unit'].lower() if data.get('unit') else None
        self.calories = float(data['calories']) if data.get(
            'calories') else None
        self.fat = float(data['fat']) if data.get('fat') else None
        self.carbs = float(data['carbs']) if data.get('carbs') else None
        self.protein = float(data['protein']) if data.get('protein') else None

    def __repr__(self) -> str:
        return f"{self.name}: {self.description}"


# залогировать успешное получение токена
async def get_fatsecret_token():
    client_id = FATSECRET_CLIENT_ID
    client_secret = FATSECRET_CLIENT_SECRET

    url = 'https://oauth.fatsecret.com/connect/token'
    data = {
        'grant_type': 'client_credentials',
        'scope': 'premier',
    }

    # Using aiohttp's BasicAuth helper
    auth = aiohttp.BasicAuth(client_id, client_secret)

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                # print(f"Token: {token_data.get('access_token')}")
                return token_data.get('access_token')
            else:
                # print(f"Error: {response.status}")
                error_text = await response.text()
                # print(f"Error details: {error_text}")
                return None


async def get_top_n_positions(query: str, token: str, n: int = 5) -> List[Food] | None:
    url = 'https://platform.fatsecret.com/rest/foods/server.api'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'method': 'foods.search.v4',
        'format': 'json',
        'search_expression': query,
        'max_results': n,
        'region': 'RU',
        'language': 'ru',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                response_dict = await response.json()
                food_dict = response_dict['foods_search']['results']['food']
                print(food_dict[0])
                return [Food(obj['food_name'], obj['food_description']) for obj in food_dict]
            else:
                print(f"Error: {response.status}")
                error_text = await response.text()
                print(f"Error details: {error_text}")
                return None


async def update_token(dp: Dispatcher) -> None:
    new_token = await get_fatsecret_token()
    if new_token:
        dp.fatsecret_token = new_token
    else:
        print("Failed to update token")


token = asyncio.run(get_fatsecret_token())
positions = asyncio.run(get_top_n_positions('Cheese', token=token))
print(positions)
