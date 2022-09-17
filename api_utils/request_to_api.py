import logging
import requests
from config_utils.config import HEADERS


def make_request(url, querystring, headers=HEADERS) -> requests.Response:
    """Отправляем запрос к API, возвращаем успешный результат или None"""
    
    logging.info(f"Call: request_to_api.make_request()")
    logging.debug(locals())
    try:
        response = requests.get(
            url=url,
            params=querystring,
            headers=headers,
            timeout=20
        )
        if response.status_code != requests.codes.ok:
            response = None

        logging.debug(f"Return: request_to_api.make_request ->\n{response}")
        return response
    except Exception as e:
        logging.warning(f'API request error: {e}')
        return None
        
