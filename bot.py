import telebot
from config_utils import config


bot = telebot.TeleBot(token=config.BOT_TOKEN)
