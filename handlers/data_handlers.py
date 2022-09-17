"""
Этот модуль для создания обработчиков для разных команд.

Для последовательной получения, проверки и обработки данных
в run_handlers передается объект для хранения данных по ключу,
список обработчиков и сообщений, которые должны выводится перед ними,
и функцию, которая должна будет выполниться после получения всех данных.
Например:

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
"""

import logging
from typing import Callable
from bot import bot
import re
from functools import partial
from api_utils import get_cities
from config_utils import MAX_HOTELS_COUNT, MAX_PHOTOS_COUNT, MESSAGES
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import datetime


def is_cancel(message: Message):
    """Если сообщение является командой отмены, 
    оправляет сообщение об отмене и возвращает True"""

    if message.text == "/cancel":
        bot.reply_to(message, MESSAGES["cancel"])
        return True
    return False


def run_handlers(message: Message, data: dict, handlers: list[tuple[Callable, str]], endpoint: Callable):
    """Добавляет конечный обработчик в список обработчиков 
    и устанавливает первый обработчик
    """
    logging.info(f"Call: data_handlers.run_handlers({locals()})")
    # добавляем в список обработчиков последний обработчик
    # в set_next_handler он будет вызываться как функция
    handlers.append(endpoint)
    handlers.reverse()
    set_next_handler(data, handlers, message.chat.id)


def set_next_handler(data: dict, handlers: list[Callable], chat_id: int):
    """Получает следующий обработчик из списка и устанавливает для следующего шага"""
    handler, msg = handlers.pop()
    logging.info(f"Call: data_handlers.set_next_handler()")
    logging.debug(f"Call: data_handlers.set_next_handler({locals()})")
    logging.info(
        f"data_handlers.set_next_handler: {handler = }, is_handlers_empty = {not bool(handlers)}")
    if msg is not None:
        bot.send_message(chat_id, msg)
    bot.clear_step_handler_by_chat_id(chat_id)
    if not handlers:
        handler(data.copy(), chat_id)
    else:
        bot.register_next_step_handler_by_chat_id(
            chat_id,
            partial(handler, data.copy(), handlers.copy())
        )


def get_city(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения города.
    Проверяет отмену, ищет города. 
    Если города найдены, выводим список кнопок, 
    иначе сообщает об ошибке и запрашивает снова.
    Устанавливает локальный обработчик нажатия кнопок, чтобы запомнить data
    """
    logging.info(f"Call: data_handlers.get_city({message.text = })")
    if is_cancel(message):
        return

    city = message.text
    cities = get_cities(city)
    if cities:
        markup = InlineKeyboardMarkup(row_width=1)
        for city in cities:
            markup.add(
                InlineKeyboardButton(
                    text=city["city_name"],
                    callback_data=f"choose_city$${city['city_id']}"
                )
            )
        bot.send_message(
            message.chat.id,
            MESSAGES["success_cities"],
            reply_markup=markup
        )
    else:
        bot.reply_to(message, MESSAGES["cities_error"])
        bot.register_next_step_handler(
            message,
            partial(get_city, data, next_handlers)
        )

    def cb_filter(c): 
        return c.data.startswith("choose_city") and c.message.chat.id == message.chat.id

    @bot.callback_query_handler(cb_filter)
    def choose_city(callback: CallbackQuery):
        """Обработчик кнопки выбора города.
        Получает city_id и записывает в data["city_id"]. Устанавливает обработчик получения даты заезда
        """
        for ch in bot.callback_query_handlers:
            if ch["filters"]["func"] == cb_filter:
                bot.callback_query_handlers.remove(ch)
                break
        city_id = int(callback.data.split("$$")[1])
        data["city_id"] = city_id
        set_next_handler(data, next_handlers.copy(), message.chat.id)


def get_start_date(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения даты заезда.
    Проверяет отмену, получает дату.
    Если формат даты верный, записывает в data["start_date"] 
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """
    logging.info(f"Call: data_handlers.get_start_date({message.text = })")
    if is_cancel(message):
        return

    try:
        start_date = datetime.datetime.strptime(
            message.text, "%d/%m/%Y"
        ).date()
        data["start_date"] = start_date
        set_next_handler(data, next_handlers, message.chat.id)
    except ValueError:
        bot.reply_to(message, MESSAGES["get_date_error"])
        bot.register_next_step_handler(
            message,
            partial(get_start_date, data, next_handlers)
        )


def get_end_date(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения даты выезда.
    Проверяет отмену, получает дату.
    Если формат даты верный, записывает в data["end_date"] 
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_end_date({message.text = })")
    if is_cancel(message):
        return

    try:
        end_date = datetime.datetime.strptime(message.text, "%d/%m/%Y").date()
        if "start_date" in data and end_date <= data["start_date"]:
            raise ValueError
        data["end_date"] = end_date
        set_next_handler(data, next_handlers, message.chat.id)
    except ValueError:
        bot.reply_to(message, MESSAGES["get_date_error"])
        bot.register_next_step_handler(
            message,
            partial(get_end_date, data, next_handlers)
        )


def get_adults_count(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения количества взрослых.
    Проверяет отмену, получает количество.
    Если формат данных верный, записывает в data["adults_count"] 
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_adults_count({message.text = })")
    if is_cancel(message):
        return

    try:
        adults = int(message.text)
        if adults > 3:
            raise ValueError()

        data["adults_count"] = adults
        set_next_handler(data, next_handlers, message.chat.id)
    except ValueError:
        bot.reply_to(message, MESSAGES["adults_count_error"])
        bot.register_next_step_handler(
            message,
            partial(get_adults_count, data, next_handlers)
        )


def get_children_age(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения количества детей.
    Проверяет отмену, получает детей в формате <возраст1, возраст2 ...> или 0 для пропуска.
    Если формат данных верный, записывает в data["children_age"] 
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_children_age({message.text = })")
    if is_cancel(message):
        return

    try:
        children = message.text
        if children == "0":
            children = None
        else:
            children_lst = children.split(",")
            for i_child in children_lst:
                if int(i_child) > 13:
                    raise ValueError()

        data["children_age"] = children
        set_next_handler(data, next_handlers, message.chat.id)
    except ValueError:
        bot.reply_to(message, MESSAGES["children_age_error"])
        bot.register_next_step_handler(
            message,
            partial(get_adults_count, data, next_handlers)
        )


def get_hotels_count(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения количества выводимых отелей.
    Проверяет отмену, получает количество.
    Если формат данных верный, записывает в data["hotels_count"] 
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_hotels_count({message.text = })")
    if is_cancel(message):
        return

    try:
        hotels_count = int(message.text)
        if hotels_count > MAX_HOTELS_COUNT:
            raise ValueError()
        data["hotels_count"] = hotels_count
        set_next_handler(data, next_handlers, message.chat.id)
    except ValueError:
        bot.reply_to(message, MESSAGES["hotels_count_error"])
        bot.register_next_step_handler(
            message,
            partial(get_hotels_count, data, next_handlers)
        )


def get_photos_count(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения количества выводимых фотографий для отелей.
    Проверяет отмену, получает количество.
    Если формат данных верный, записывает в data["photos_count"] 
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_photos_count({message.text = })")
    if is_cancel(message):
        return

    try:
        photos_count = int(message.text)
        if photos_count > MAX_PHOTOS_COUNT:
            raise ValueError()

        data["photos_count"] = photos_count
        set_next_handler(data, next_handlers, message.chat.id)
    except ValueError:
        bot.reply_to(message, MESSAGES["photos_count_error"])
        bot.register_next_step_handler(
            message,
            partial(get_photos_count, data, next_handlers)
        )


def get_currency(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения валюты.
    Проверяет отмену, получает валюту.
    Если формат данных верный, записывает в data["currency"]
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_currency({message.text = })")
    if is_cancel(message):
        return

    currency = message.text
    pattern = r"[A-Za-z]{3}\b"
    if re.match(pattern, currency):
        currency = currency.upper()
        data["currency"] = currency
        set_next_handler(data, next_handlers, message.chat.id)
    else:
        bot.reply_to(message, MESSAGES["currency_error"])
        bot.register_next_step_handler(
            message,
            partial(get_currency, data, next_handlers)
        )


def get_prices_range(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения диапазона цен.
    Проверяет отмену, получает диапазон.
    Если формат данных верный, записывает в data["price_min"] и data["price_max"]
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_price_range({message.text = })")
    if is_cancel(message):
        return

    prices = message.text
    try:
        price_min, price_max = prices.split("-")
        price_min, price_max = int(price_min), int(price_max)
        data["price_min"] = price_min
        data["price_max"] = price_max
        set_next_handler(data, next_handlers, message.chat.id)
    except:
        bot.reply_to(message, MESSAGES["prices_range_error"])
        bot.register_next_step_handler(
            message,
            partial(get_prices_range, data, next_handlers)
        )


def get_distances_range(data: dict, next_handlers: list[Callable], message: Message):
    """Обработчик получения диапазона цен.
    Проверяет отмену, получает диапазон.
    Если формат данных верный, записывает в data["distance_min"] и data["distance_max"]
    и устанавливает следующий обработчик, 
    иначе сообщает об ошибке и запрашивает снова
    """

    logging.info(f"Call: data_handlers.get_distance_range({message.text = })")
    if is_cancel(message):
        return

    distances = message.text
    try:
        distance_min, distance_max = distances.split("-")
        distance_min, distance_max = int(distance_min), int(distance_max)
        data["distance_min"] = distance_min
        data["distance_max"] = distance_max
        set_next_handler(data, next_handlers, message.chat.id)
    except:
        bot.reply_to(message, MESSAGES["distances_range_error"])
        bot.register_next_step_handler(
            message,
            partial(get_distances_range, data, next_handlers)
        )
