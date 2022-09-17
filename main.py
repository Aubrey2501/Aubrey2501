from bot import bot
import handlers
import logging

logging.basicConfig(level=logging.DEBUG)

loggers = logging.Logger.manager.loggerDict
for k in loggers:
    if not 'pkg' in k:
        loggers[k].disabled = True

logging.getLogger("exchangelib.folders").disabled = True
logging.getLogger("exchangelib.services").disabled = True


if __name__ == "__main__":
    bot.polling(non_stop=True)
