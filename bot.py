from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from consts import Constants
import logging
import os
import sys

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv('PORT', '8443'))
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Normal", callback_data='1'),
            InlineKeyboardButton("Anonymous", callback_data='2')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(Constants.INTRODUCTION, reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")

# add handlers
dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

# start webhook
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://captain-capsule.herokuapp.com/" + TOKEN)
updater.idle()