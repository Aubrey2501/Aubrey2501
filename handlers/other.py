from bot import bot
from config_utils import MESSAGES
from telebot.types import Message


@bot.message_handler()
def other(message: Message):
    bot.reply_to(message, MESSAGES["other"])
