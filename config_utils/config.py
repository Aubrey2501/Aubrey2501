import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")
HEADERS = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": RAPID_API_HOST}
LOCATIONS_URL = "https://hotels4.p.rapidapi.com/locations/v2/search"
PROPERTIES_URL = "https://hotels4.p.rapidapi.com/properties/list"
PHOTOS_URL = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
HOTEL_DETAILS_URL = "https://hotels4.p.rapidapi.com/properties/get-details"

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("lowprice", "Топ самых дешевых отелей в городе"),
    ("highprice", "Топ самых дорогих отелей в городе"),
    ("bestdeal", "Топ самых близких к центру города отелей"),
    ("history", "Список выполненных команд")
)

MAX_HOTELS_COUNT = 25
MAX_PHOTOS_COUNT = 10

CANCEL_TEXT = "\nДля отмены нажмите /cancel"


