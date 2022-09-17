import json
import logging

from config_utils.config import HEADERS, PROPERTIES_URL
from requests import Response

from api_utils.request_to_api import make_request


def get_hotels(
    city_id: str,
    dates: tuple,
    adults: int,
    children: str,
    hotels_count: int,
    currency: str,
    sort_order: str,
    price_min: int,
    price_max: int
) -> list:
    """Формируем список отелей из данных API"""

    logging.info(f"Call: find_hotels.get_hotels({locals()})")
    response = request_hotels(
        city_id,
        dates,
        adults,
        children,
        hotels_count,
        currency,
        sort_order,
        price_min,
        price_max
    )
    hotels = []
    if response is not None:
        data = json.loads(response.text)
        if data["result"] == "OK":
            hotels = data["data"]["body"]["searchResults"]["results"]

    logging.debug(f"Return: find_hotels.get_hotels ->\n{hotels}")
    return hotels


def request_hotels(
    city_id: str,
    dates: tuple,
    adults: int,
    children: str,
    hotels_count: int,
    currency: str,
    sort_order: str,
    price_min: int,
    price_max: int
) -> Response:
    """Строим запрос и получаем данные по API"""

    querystring = {
        "destinationId": city_id,
        "pageNumber": "1",
        "pageSize": str(hotels_count),
        "checkIn": str(dates[0]),
        "checkOut": str(dates[1]),
        "adults1": str(adults),
        "children1": children,
        "sortOrder": sort_order,
        "locale": "ru_RU",
        "currency": currency
    }
    if price_min is not None:
        querystring["priceMin"] = price_min
    if price_min is not None:
        querystring["priceMax"] = price_max
    
    if sort_order == "DISTANCE_FROM_LANDMARK":
        querystring["landmarkIds"] = 'City_center'
        
    return make_request(url=PROPERTIES_URL, headers=HEADERS, querystring=querystring)
