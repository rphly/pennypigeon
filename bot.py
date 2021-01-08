from enum import Enum
from uuid import uuid4
import re
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
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
import pyrebase
from consts import Constants
import logging
import os
import sys
from dotenv import load_dotenv

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


def start(update: Update, context: CallbackContext):

    # save user context
    user = update.message.from_user["username"]
    user_id = update.message.from_user["id"]
    chat_id = update.message.chat_id
    context.user_data["user"] = user
    context.user_data["chat_id"] = chat_id

    # check if exists
    if not is_known_user(user):
        print("creating user")
        db.child("users").child(user).set({
            "inbox": None,
            "chat_id": chat_id,
            "user_id": user_id
        })  # initialize inbox

    # TODO: check for existing unread messages in inbox

    # continue
    update.message.reply_text(Constants.INTRODUCTION)


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


def skip_image(update: Update, context: CallbackContext):

    update.message.reply_text("Okay so just a message yeah?")
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"], text="Okay so just a message yeah?")
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.SEND_MESSAGE)
    return MESSAGE


def handle_message(update: Update, context: CallbackContext):

    context.user_data["message"] = update.message.text
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"],
        text=Constants.RECEIVED_MESSAGE)
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"], text=Constants.GET_RECEIVER)
    return USERNAME


def handle_username(update: Update, context: CallbackContext):
    username = update.message.text.replace("@", "")
    print("handling username: " + username)
    if username and is_known_user(username):
        context.user_data["receiver"] = username
    elif not is_known_user(username):
        updater.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=Constants.FRIEND_NOT_FOUND.format(username))
        updater.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=Constants.INVITE_FRIEND)

    save_to_db_and_trigger_send_message(update, context)

    return ConversationHandler.END


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
        "image_url": None
    }

    if "image" in data:
        # store the image
        f = updater.bot.get_file(data["image"])
        im = f.download_as_bytearray()
        # im = Image.open(BytesIO(im_array))
        # output = BytesIO()
        # output.name = 'image.jpgg'
        # im.save(output, 'JPEG')
        # output.seek(0)
        filename = f"{data['image']}.jpg"
        loc = f"{receiver_username}/{filename}"
        storage.child(loc).put(im)

        # get url and add to base_message
        file_url = storage.child(loc).get_url(token=TOKEN)
        base_message["image_url"] = file_url

    db.child("users").child(receiver_username).child(
        "inbox").push(base_message)  # append to inbox

    print(base_message)
    # try trigger message to user

    receiver = db.child("users").child(receiver_username).get().val()
    if receiver:
        location = data["location"]
        alert = Constants.ANONYMOUS_ALERT.format(
            location["lat"], location["long"]) if data["mode"] == Mode.ANONYMOUS else Constants.NORMAL_ALERT.format(data["receiver"], location["lat"], location["long"])

        updater.bot.send_message(
            chat_id=receiver["user_id"], text=alert)

    # done
    updater.bot.send_message(
        chat_id=context.user_data["chat_id"], text=Constants.DONE.format(context.user_data["receiver"]))


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
    dispatcher.add_handler(CommandHandler('start', start))

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
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
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    print("up")
    updater.bot.set_webhook("https://captain-capsule.herokuapp.com/" + TOKEN)
    # updater.start_polling()
    # print("Polling...")
    updater.idle()


main()
