import json
import logging
import re

from config_utils.config import HEADERS, LOCATIONS_URL
from requests import Response

from api_utils.request_to_api import make_request


def get_cities(city: str):
    """Фильтруем данные, полученные по API, и возвращаем список городов"""

    logging.info(f"Call: find_cities.get_cities({city})")
    response = request_city(city)
    cities = []
    if response is not None:
        pattern = r"""(?<="CITY_GROUP",).+?[\]]"""
        find = re.search(pattern, response.text)
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")
            for i_destination in suggestions["entities"]:
                clear_destination = re.sub("<.*?>", "", i_destination["caption"])
                cities.append({"city_name": clear_destination,
                            "city_id": i_destination["destinationId"]})

    logging.debug(f"Return: find_cities.get_cities ->\n{cities}")
    return cities


def request_city(city: str) -> Response:
    """Строим запрос и получаем данные по API"""
    querystring = {"query": city, "locale": "ru_RU", "currency": "USD"}
    return make_request(url=LOCATIONS_URL, headers=HEADERS, querystring=querystring)
