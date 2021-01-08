class Constants:
    INTRODUCTION = """Coo coo🐦 I'm PennyPigeon and I help watch over messages you leave in locations for your friends, family and loved ones to uncover!\nIf you've received a message, simply travel to the coordinates and share your location to read it!

    To leave a note, use the command /send and /cancel to exit whenever. 
    You can also list all unread messages with /show_unread and uncover messages others have left for you at different locations with /uncover.\n
    
    start - start the bot\n
    send - leave a message somewhere!\n
    uncover - read all messages at a location\n
    show_unread - show all unread messages\n
    cancel - exit the process
    """

    # Select Mode
    SELECT_MODE = """
    You want to send a:
    """
    ANONYMOUS_MODE = """You selected: Anonymous Message \nShhhH!🤫 Okay... we won't let them know who you are... we promise!"""
    NORMAL_MODE = """You selected: Normal Message \nGot it 👍!"""

    # Location
    SEND_LOCATION = """Where do you want to leave your message? Share your location to let us know."""
    RECEIVED_LOCATION = """Alright, we've got the location."""

    # Send message/image
    SEND_IMAGE = """Send me the image you want me to leave here for the receiver! (use /skip if you don't have an image)"""
    SEND_MESSAGE = """Send me the message you want me to leave here for the receiver!"""
    RECEIVED_MESSAGE = """Nice, you are almost there!"""
    RECEIVED_IMAGE = """Looking good, I'm sure they will love it."""

    # GET RECEIVER
    GET_RECEIVER = """Alright, who are we leaving this message for? (Use their username eg. @waishun2)"""

    # FRIEND NOT KNOWN TO BOT
    FRIEND_NOT_FOUND = """It seems like your friend @{} hasn't been acquainted with @PennyPigeon. Forward the following message to him so he can start receiving messages!"""
    INVITE_FRIEND = """Hey there! It appears someone has left you a message on @pennypigeon_bot. To receive it, start a chat with: t.me/pennypigeon_bot"""

    # DONE
    DONE = """Proceeds to lay a nest while waiting for @{} to uncover your message at location!"""

    TELEGRAM_USERNAME_REGEX = '^@[a-z0-9\_]{5,32}$'

    # ALERT
    NORMAL_ALERT = """@{} has just left you a message at http://maps.google.com/?q={},{} ! Make your way to uncover it 😲!"""
    ANONYMOUS_ALERT = """A certain someone has just left you a message at http://maps.google.com/?q={},{} ! Go there to find out the message 😏!"""

    RANDOM_ACTIONS = [
        "You turn over a rock to uncover....\n\n",
        "You look into the tree hollow...! You found something: \n\n",
        "What's that over there... It looks like someone left something on the ground\n\n",
        "You look up and a package gently falls into your lap... \n\n",
        "Etched on a stone, you see... \n\n",
        "You find a letter floating in the wind... \n\n"
    ]
