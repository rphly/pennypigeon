from enum import Enum
from uuid import uuid4
import random
import re
import json
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ChatAction
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
import geopy.distance
import pyrebase
from consts import Constants
import logging
import os
import sys
from dotenv import load_dotenv
import time
from functools import wraps

load_dotenv()

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = os.getenv("BOT_TOKEN")
updater = Updater(TOKEN, use_context=True)

PORT = int(os.getenv('PORT', '8443'))

config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "storageBucket": os.getenv("STORAGE_BUCKET")
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()


class Mode():
    ANONYMOUS = "ANONYMOUS_MODE"
    NORMAL = "NORMAL_MODE"


MODE, LOCATION, IMAGE, MESSAGE, USERNAME = range(5)
READ_LOCATION = 0
ONBOARD_LOCATION = 0


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


@send_typing_action
def start(update: Update, context: CallbackContext):

    # save user context
    user = update.message.from_user["username"]
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat_id
    context.user_data["user"] = user
    context.user_data["chat_id"] = chat_id

    # check if exists
    if not is_known_user(user):
        db.child("users").child(user).set({
            "chat_id": chat_id,
            "user_id": user_id
        })
    else:
        # known
        db.child("users").child(user).update({
            "chat_id": chat_id,
            "user_id": user_id
        })

    location_keyboard = KeyboardButton(
        text="Send Location", request_location=True)

    reply_markup = ReplyKeyboardMarkup(
        [[location_keyboard]], one_time_keyboard=True)

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.ONBOARDING,
        reply_markup=reply_markup)

    return ONBOARD_LOCATION


@send_typing_action
def handle_location_onboard(update: Update, context: CallbackContext):
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text="Got it... Opening the message...",
        reply_markup=ReplyKeyboardRemove(
            remove_keyboard=True
        )
    )
    time.sleep(1)

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.INTRODUCTION,
    )

    check_unread(update, context)

    return ConversationHandler.END


@send_typing_action
def check_unread(update: Update, context: CallbackContext):
    user = update.message.from_user["username"]
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat_id
    context.user_data["user"] = user
    context.user_data["chat_id"] = chat_id

    unread_messages = db.child("users").child(context.user_data["user"]).child(
        "inbox").order_by_child("unread").equal_to(True).get().val()

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text="""You have {} unread messages.""".format(len(unread_messages)))

    for key in unread_messages:
        message = unread_messages[key]
        alert = get_formatted_alert(message)
        updater.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=alert,)


@send_typing_action
def send(update: Update, context: CallbackContext):
    user = update.message.from_user["username"]
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat_id
    context.user_data["user"] = user
    context.user_data["chat_id"] = chat_id

    keyboard = [
        [
            InlineKeyboardButton("Normal", callback_data=Mode.NORMAL),
            InlineKeyboardButton("Anonymous", callback_data=Mode.ANONYMOUS)
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(Constants.SELECT_MODE,
                              reply_markup=reply_markup)
    return MODE


@send_typing_action
def read(update: Update, context: CallbackContext):
    user = update.message.from_user["username"]
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat_id
    context.user_data["user"] = user
    context.user_data["chat_id"] = chat_id

    location_keyboard = KeyboardButton(
        text="Send Location", request_location=True)

    reply_markup = ReplyKeyboardMarkup(
        [[location_keyboard]], one_time_keyboard=True)

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.SEND_LOCATION,
        reply_markup=reply_markup)

    return READ_LOCATION


@send_typing_action
def handle_location_read(update: Update, context: CallbackContext):
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text="Got it... scanning the area...",
        reply_markup=ReplyKeyboardRemove(
            remove_keyboard=True
        )
    )

    location = {
        "lat": update.message.location["latitude"],
        "long": update.message.location["longitude"],
    }

    messages = db.child("users").child(context.user_data["user"]).child(
        "inbox").get().val()

    for key in messages:
        message = messages[key]
        if message["unread"] and within(message["location"], location):
            updater.bot.send_message(
                chat_id=context.user_data["chat_id"],
                text="""You have {} messages hidden at this location.""".format(
                    len(messages)),
            )

            action = random.choice(Constants.RANDOM_ACTIONS)
            sender = "@" + \
                message["sender"] if message["mode"] == Mode.NORMAL else "Someone"

            text = f"""{action}\n\n{message["message"]}\n\n-- From {sender}"""

            if "image" in message:
                updater.bot.send_photo(
                    chat_id=context.user_data["chat_id"],
                    photo=message["image"],
                    caption=text)
            else:
                updater.bot.send_message(
                    chat_id=context.user_data["chat_id"],
                    text=text)

            # mark as read
            db.child("users").child(context.user_data["user"]).child("inbox").child(key).update({
                "unread": False
            })

    return ConversationHandler.END


@send_typing_action
def handle_mode(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()

    if query.data in [Mode.ANONYMOUS, Mode.NORMAL]:
        context.user_data["mode"] = query.data
        query.edit_message_text(text=Constants.ANONYMOUS_MODE if query.data ==
                                Mode.ANONYMOUS else Constants.NORMAL_MODE)

    location_keyboard = KeyboardButton(
        text="Send Location", request_location=True)

    reply_markup = ReplyKeyboardMarkup(
        [[location_keyboard]], one_time_keyboard=True)

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.SEND_LOCATION,
        reply_markup=reply_markup)

    return LOCATION


@send_typing_action
def handle_location(update: Update, context: CallbackContext):

    context.user_data["location"] = {
        "lat": update.message.location["latitude"],
        "long": update.message.location["longitude"]
    }
    update.message.reply_text(Constants.RECEIVED_LOCATION,
                              reply_markup=ReplyKeyboardRemove(
                                  remove_keyboard=True
                              ),)
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.SEND_IMAGE)
    return IMAGE


@send_typing_action
def handle_image(update: Update, context: CallbackContext):

    fileid = update.message.photo[-1].file_id

    context.user_data["image"] = fileid

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.RECEIVED_IMAGE)
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.SEND_MESSAGE)
    return MESSAGE


@send_typing_action
def skip_image(update: Update, context: CallbackContext):

    update.message.reply_text("Okay so just a message yeah?")

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.SEND_MESSAGE)
    return MESSAGE


@send_typing_action
def handle_message(update: Update, context: CallbackContext):

    context.user_data["message"] = update.message.text
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.RECEIVED_MESSAGE)
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"], text=Constants.GET_RECEIVER)
    return USERNAME


@send_typing_action
def handle_username(update: Update, context: CallbackContext):
    username = update.message.text.replace("@", "")
    print("handling username: " + username)
    if username:
        context.user_data["receiver"] = username

    if not is_known_user(username):
        updater.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=Constants.FRIEND_NOT_FOUND.format(username))
        updater.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=Constants.INVITE_FRIEND)

    save_to_db_and_trigger_send_message(update, context)

    return ConversationHandler.END


@send_typing_action
def save_to_db_and_trigger_send_message(update: Update, context: CallbackContext):
    print("doing firebase stuff")
    # do firebase stuff
    data = context.user_data
    receiver_username = data["receiver"]
    base_message = {
        "message": data["message"],
        "location": data["location"],
        "unread": True,
        "sender": data["user"],
        "image": data.get("image", None),
        "mode": data["mode"]
    }

    updater.bot.send_message(
        chat_id=context.user_data["chat_id"], text="Doing some final checks...")

    db.child("users").child(receiver_username).child(
        "inbox").push(base_message)  # append to inbox

    # try trigger message to user
    receiver = db.child("users").child(receiver_username).get().val()
    if receiver and "user_id" in receiver and receiver["user_id"]:
        alert = get_formatted_alert(base_message)
        updater.bot.send_message(
            chat_id=receiver["user_id"], text=alert)

    # done
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"], text=Constants.DONE.format(context.user_data["receiver"]))


def within(location1, location2):
    coords1 = (location1["lat"], location1["long"])
    coords2 = (location2["lat"], location2["long"])
    return geopy.distance.distance(coords1, coords2).meters < 20


def get_formatted_alert(data):
    location = data["location"]
    alert = Constants.ANONYMOUS_ALERT.format(
        location["lat"], location["long"]) if data["mode"] == Mode.ANONYMOUS else Constants.NORMAL_ALERT.format(data["sender"], location["lat"], location["long"])
    return alert


def is_known_user(username):
    # check firebase
    return db.child("users").child(username).shallow().get().val()


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Maybe next time then! :)', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    print("starting bot")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('show_unread', check_unread))

    onboarding_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ONBOARD_LOCATION: [
                MessageHandler(Filters.location, handle_location_onboard)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(onboarding_handler)

    read_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('uncover', read)],
        states={
            READ_LOCATION: [
                MessageHandler(Filters.location, handle_location_read)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(read_conv_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send)],
        states={
            MODE: [CallbackQueryHandler(handle_mode)],
            IMAGE: [
                MessageHandler(Filters.photo, handle_image), CommandHandler('skip', skip_image), ],
            LOCATION: [
                MessageHandler(Filters.location, handle_location)
            ],
            MESSAGE: [MessageHandler(Filters.text, handle_message)],
            USERNAME: [MessageHandler(Filters.regex(Constants.TELEGRAM_USERNAME_REGEX), handle_username)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    # start webhook
    updater.bot.set_webhook("https://captain-capsule.herokuapp.com/" + TOKEN)
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.idle()
    # print("up")
    # updater.start_polling()
    # print("Polling...")


main()
