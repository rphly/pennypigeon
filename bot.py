from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from consts import Constants
import logging
import os
import sys

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv('PORT', '8443'))
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=Constants.INTRODUCTION)

# define handlers
start_handler = CommandHandler('start', start)

# add handlers
dispatcher.add_handler(start_handler)

# start webhook
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://captain-capsule.herokuapp.com/" + TOKEN)
updater.idle()