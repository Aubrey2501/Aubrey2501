import json
import logging
import re

from config_utils.config import HEADERS, HOTEL_DETAILS_URL
from requests import Response

from api_utils.request_to_api import make_request


def get_hotel_details(
    hotel_id: int
) -> dict:
    """Формируем данные об отеле из данных API"""

    logging.info(f"Call: hotel_details.get_hotel_details({locals()})")
    response = request_hotels(hotel_id)

    hotel_details = {}
    if response is not None:
        data = json.loads(response.text)["data"]["body"]

        try:
            price = data["propertyDescription"]["featuredPrice"]["currentPrice"]["formatted"]
        except:
            price = ""
        try:
            row_price = data["propertyDescription"]["featuredPrice"]["currentPrice"]["plain"]
        except:
            row_price = ""
        try:
            rating = data["propertyDescription"]["starRating"]
        except:
            rating = ""
        try:
            address = data["propertyDescription"]["address"]["fullAddress"]
        except:
            address = ""

        try:
            overview_sections = data["overview"]["overviewSections"]
            overview = "Overview:\n\n"
            for ow_section in overview_sections:
                title = ow_section.get("title", "")
                if title:
                    content = "- " + "\n- ".join(ow_section.get("content", []))
                    overview += f"{title}:\n{content}\n\n"
        except:
            overview = ""

        hotel_details = {
            "price": price, 
            "row_price": row_price,
            "rating": rating, 
            "address": address, 
            "overview": overview
        }
    
    logging.debug(
        f"Return: hotel_details.get_hotel_details ->\n{hotel_details}"
    )
    return hotel_details


def request_hotels(hotel_id: int) -> Response:
    """Строим запрос и получаем данные по API"""

    querystring = {"id": hotel_id}
    return make_request(url=HOTEL_DETAILS_URL, headers=HEADERS, querystring=querystring)


