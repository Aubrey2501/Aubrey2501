from bot import bot
from telebot.types import Message
from config_utils import MESSAGES


@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
    bot.reply_to(
        message, 
        MESSAGES["start"].format(message.from_user.full_name)
    )
