from datetime import datetime

from bot import bot
from config_utils import MESSAGES
from telebot.types import Message
from . import common_handlers, data_handlers


@bot.message_handler(commands=["lowprice"])
def cmd_lowprice(message: Message):
    bot.reply_to(message, MESSAGES["lowprice"])
    data = {
        "cmd": "lowprice",
        "cmd_time": datetime.now(),
        "sort_order": "PRICE"
    }
    data_handlers.run_handlers(
        message,
        data,
        [
            (data_handlers.get_city, MESSAGES["get_city"]),
            (data_handlers.get_start_date, MESSAGES["get_start_date"]),
            (data_handlers.get_end_date, MESSAGES["get_end_date"]),
            (data_handlers.get_adults_count, MESSAGES["get_adults_count"]),
            (data_handlers.get_children_age, MESSAGES["get_children_age"]),
            (data_handlers.get_hotels_count, MESSAGES["get_hotels_count"]),
            (data_handlers.get_photos_count, MESSAGES["get_photos_count"]),
            (data_handlers.get_currency, MESSAGES["get_currency"]),
        ],
        (common_handlers.show_hotels, MESSAGES["show_hotels"])
    )
