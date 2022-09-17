from bot import bot
from config_utils import MESSAGES
from telebot.types import Message


@bot.message_handler(commands=["help"])
def cmd_help(message: Message):
    bot.reply_to(message, MESSAGES["help"])
