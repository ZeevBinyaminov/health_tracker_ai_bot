import asyncio
from typing import List
import json

import aiohttp
from aiogram import Dispatcher


from config import FATSECRET_CLIENT_ID, FATSECRET_CLIENT_SECRET

_TOKEN_CACHE = {"value": None}


class Food:
    def __init__(self, food_name: str, servings: list[dict]) -> None:
        self.name = food_name
        self.parse_servings(servings)

    def parse_servings(self, servings: list[dict]) -> None:
        for serving in servings:
            if serving['metric_serving_unit'] == 'g':
                self.amount = 100
                self.unit = serving['metric_serving_unit']
                self.calories = int(
                    float(serving['calories']) / float(serving['metric_serving_amount']) * 100)
                self.fat = float(serving['fat'])
                self.carbs = float(serving['carbohydrate'])
                self.protein = float(serving['protein'])
                break

    def __repr__(self) -> str:
        return f"{self.name}: {self.calories} kcal for {self.amount}{self.unit}" \
            f"({self.fat}g fat, {self.carbs}g carbs, {self.protein}g protein)"


# залогировать успешное получение токена
async def get_fatsecret_token():
    client_id = FATSECRET_CLIENT_ID
    client_secret = FATSECRET_CLIENT_SECRET

    url = 'https://oauth.fatsecret.com/connect/token'
    data = {
        'grant_type': 'client_credentials',
        'scope': 'premier',
    }

    auth = aiohttp.BasicAuth(client_id, client_secret)

    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                return token_data.get('access_token')
            else:
                error_text = await response.text()
                return None


async def get_top_n_positions(query: str, n: int = 10) -> List[Food]:
    url = 'https://platform.fatsecret.com/rest/foods/server.api'
    token = get_cached_token()
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
                total_results = int(
                    response_dict['foods_search']['total_results'])
                if total_results == 0:
                    return []
                food_dict = response_dict['foods_search']['results']['food']

                food_list = []
                for obj in food_dict:
                    in_grams = any([serving.get(
                        'metric_serving_unit') == 'g' for serving in obj['servings']['serving']])
                    if in_grams:
                        food_obj = Food(obj['food_name'],
                                        obj['servings']['serving'])
                        food_list.append(food_obj)
                return food_list

            else:
                print(f"Error: {response.status}")
                error_text = await response.text()
                print(f"Error details: {error_text}")
                return []


def get_cached_token() -> str | None:
    return _TOKEN_CACHE["value"]


def set_cached_token(token: str | None) -> None:
    _TOKEN_CACHE["value"] = token


async def update_token() -> None:
    new_token = await get_fatsecret_token()
    if new_token:
        set_cached_token(new_token)
        return new_token
