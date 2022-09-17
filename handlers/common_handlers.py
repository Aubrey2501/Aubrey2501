import logging
from api_utils import get_hotels, get_photos
from bot import bot
from config_utils import MESSAGES
from database.db_utils import add_history_row
from telebot.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, InputMediaPhoto, Message)


def show_hotels(data: dict, chat_id: int, hotels_handlers={}):
    """Ищет подходящие отели по заданным параметрам и 
    выводим пользователю список кнопок с краткой информацией об отелях.
    Определяем обработчик для кнопок с отелями
    """

    # замыкание, для обработки кнопок с доступом к hotels
    def choose_hotel(callback: CallbackQuery):
        """Обработчик выбора отеля. Выводит информацию об отеле и фотографии"""

        data = callback.data.split(",")
        hotel_id = int(data[0].split("$$")[1])
        photos_count = int(data[1].split("$$")[1])
        bot.send_message(callback.message.chat.id, "Загружаем данные...")
        for hotel in hotels:
            if hotel.get("id") == hotel_id:
                break
        name = hotel["name"]
        rating = hotel["starRating"]
        address = hotel.get("address", {}).get("streetAddress", "-")
        reviews = hotel.get("guestReviews", {}).get("unformattedRating", "н/д")
        caption = f"{name}, {rating}\U00002605\n"
        caption += f"Адрес: {address}\n"
        caption += f"Рейтинг: {reviews}/10\n"

        rate = hotel.get("ratePlan", {}).get("price", {}).get("current", None)
        if rate is not None:
            caption += f"Средняя цена: {rate} /сут.\n"

        neighbourhood = hotel.get("neighbourhood", None)
        if neighbourhood is not None:
            caption += f"Находится в районе: {neighbourhood}\n"

        total = hotel.get("ratePlan", {}).get(
            "price", {}).get("fullyBundledPricePerStay", None)
        if total is not None:
            caption += f"\nПолная цена: {total}\n".replace("&nbsp;", " ")

        landmarks = hotel.get("landmarks", None)
        if landmarks is not None:
            points = "Ближайшие места:\n"
            for landmark in landmarks:
                label = landmark["label"]
                distance = landmark["distance"]
                point = f"{label}, расстояние: {distance}\n"
                points += point
            caption += points

        caption += f'Ссылка: https://www.hotels.com/ho{hotel_id}'
        # получает фото отеля
        photos = get_photos(hotel_id, photos_count)
        if photos is not None:
            media = [InputMediaPhoto(photo) for photo in photos]
            bot.send_media_group(callback.message.chat.id, media)

        bot.send_message(callback.message.chat.id, caption)

    hotels = get_hotels(
        data["city_id"],
        (data["start_date"], data["end_date"]),
        data["adults_count"],
        data["children_age"],
        data["hotels_count"],
        data["currency"],
        data["sort_order"],
        data.get("price_min"),
        data.get("price_max"),
    )
    if "distance_min" in data:
        for hotel in hotels:
            landmarks = hotel.get("landmarks", {})
            if landmarks and landmarks[0]["label"] in ("Центр города", "City center"):
                dist = float(landmarks[0]["distance"].split()[
                             0].replace(",", "."))
                if dist < data["distance_min"]:
                    hotels.remove(hotel)

    if "distance_max" in data:
        for hotel in hotels:
            landmarks = hotel.get("landmarks", {})
            if landmarks and landmarks[0]["label"] in ("Центр города", "City center"):
                dist = float(landmarks[0]["distance"].split()[
                             0].replace(",", "."))
                if dist > data["distance_max"]:
                    hotels.remove(hotel)

    if hotels:
        add_history_row(data["cmd"], data["cmd_time"], [
                        hotel["name"] for hotel in hotels])

        bot.send_message(chat_id, "Подобрали для вас следующие отели:")
        markup = InlineKeyboardMarkup(row_width=1)
        # создает кнопки, содержащие название отеля, рейтинг и цену за сутки
        for hotel in sorted(hotels, key=lambda elem: elem.get("starRating")):
            try:
                button_text = f"{hotel['name']}, {int(hotel['starRating'])}\U00002605, " \
                              f"{hotel['ratePlan']['price']['current']} /сут."
            except KeyError:
                button_text = f"{hotel['name']}, {int(hotel['starRating'])}\U00002605, " \
                              f" цена/сут.: н/д"
            markup.add(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"choose_hotel$${hotel['id']},photos_count$${data['photos_count']}"
                )
            )
        bot.send_message(
            chat_id, MESSAGES["success_hotels"], reply_markup=markup)
    else:
        bot.send_message(chat_id, MESSAGES["no_hotels"])

    for hnd in bot.callback_query_handlers:
        if hnd['function'] == hotels_handlers.get(chat_id):
            bot.callback_query_handlers.remove(hnd)
            logging.debug(f'Remove handler {hnd} for {chat_id = }')

    hotels_handlers[chat_id] = choose_hotel
    bot.register_callback_query_handler(
        hotels_handlers[chat_id],
        lambda c: c.data.startswith(
            "choose_hotel") and c.message.chat.id == chat_id
    )
