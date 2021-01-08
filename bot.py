from enum import Enum
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Filters, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext
from consts import Constants
import logging
import os
import sys

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv('PORT', '8443'))
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

class Mode(Enum):
    ANONYMOUS = "ANONYMOUS_MODE"
    NORMAL = "NORMAL_MODE"


def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Normal", callback_data=Mode.NORMAL),
            InlineKeyboardButton("Anonymous", callback_data=Mode.ANONYMOUS)
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(Constants.INTRODUCTION, reply_markup=reply_markup)

def select_mode(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data["mode"] = query.data
    query.edit_message_text(text= Constants.ANONYMOUS_MODE if query.data == Mode.ANONYMOUS else Constants.NORMAL_MODE)
    update.message.reply_text(Constants.SEND_LOCATION)
    
    keyboard = [
        [
            KeyboardButton("Send Location", request_location=True),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

def handle_location(update: Update, context: CallbackContext):
    print(update.message.location)
    context.user_data["location"] = update.message.location
    update.message.reply_text(str(context.user_data))
    

# add handlers
dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(select_mode))
dispatcher.add_handler(MessageHandler(Filters.location, handle_location))


# start webhook
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://captain-capsule.herokuapp.com/" + TOKEN)
updater.idle()