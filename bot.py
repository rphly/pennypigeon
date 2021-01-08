from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown
from consts import Constants
import logging
import os
import sys

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv('PORT', '8443'))
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text=Constants.INTRODUCTION)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=Constants.INTRODUCTION)

def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(), title="Caps", input_message_content=InputTextMessageContent(query.upper())
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
            ),
        ),
    ]

    update.inline_query.answer(results)


# define handlers
start_handler = CommandHandler('start', start)
inline_handler = InlineQueryHandler(inlinequery)

# add handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(inline_handler)

# start webhook
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.bot.set_webhook("https://captain-capsule.herokuapp.com/" + TOKEN)
updater.idle()