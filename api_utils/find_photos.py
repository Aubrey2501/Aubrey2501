import json
import logging

from config_utils.config import HEADERS, PHOTOS_URL
from requests import Response

from api_utils.request_to_api import make_request


def get_photos(hotel_id: str, photos_count: int) -> list:
    """Получаем данные API и возвращаем список ссылок на изображения"""

    logging.info(f"Call: find_photos.get_photos({locals()})")
    response = request_photos(hotel_id)
    photos = []
    if response is not None:    
        data = json.loads(response.text)
        selection = data["hotelImages"]
        for image in selection:
            photo = image["baseUrl"].replace("{size}", "y")
            photos.append(photo)
            if len(photos) == photos_count:
                break

    logging.debug(f"Return: find_photos.get_photos ->\n{photos}")
    return photos


def request_photos(hotel_id: str) -> Response:
    """Строим запрос и получаем данные по API"""

    querystring = {"id": hotel_id}
    return make_request(url=PHOTOS_URL, headers=HEADERS, querystring=querystring)
