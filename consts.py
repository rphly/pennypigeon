class Constants:
    INTRODUCTION = """Hi there! I'm Penny Pigeon, I help users like you store messages in locations for your friends, family and loved ones to uncover!\nIf you've received a message, simply travel to the coordinates and share your location with us to read it!

    If you'd like to leave a note, use the command /send and /cancel to exit whenever. 
    You can list all unread messages with /show_unread and uncover hidden messages at a location with /uncover.
    
    Enjoy the outdoors :)
    """

    # Select Mode
    SELECT_MODE = """
    Pick a mode:
    """
    ANONYMOUS_MODE = """You selected: Anonymous Mode. \nShhhH! Okay... we won't let them know who you are... we promise!"""
    NORMAL_MODE = """You selected: Normal Mode. \nGot it!"""

    # Location
    SEND_LOCATION = """Could we get your current location please?"""
    RECEIVED_LOCATION = """Alright, we've got the location."""

    # Send message/image
    SEND_IMAGE = """Send me the image you want me to leave here for the receiver! (use /skip if you don't have an image)"""
    SEND_MESSAGE = """Send me the message you want me to leave here for the receiver!"""
    RECEIVED_MESSAGE = """Nice, thanks!"""
    RECEIVED_IMAGE = """Great picture, I'm sure they will love it."""

    # GET RECEIVER
    GET_RECEIVER = """Alright, who are we leaving this message for? (Use their username eg. @peter)"""

    # FRIEND NOT KNOWN TO BOT
    FRIEND_NOT_FOUND = """It seems like your friend @{} hasn't registered with us. Forward the following message to him so he can start receiving messages left in his inbox!"""
    INVITE_FRIEND = """Hey there! Someone's left you a message on @captain_capsule_bot. In order to receive it, you gotta start a chat with: t.me/captain_capsule_bot"""

    # DONE
    DONE = """Done, message saved for @{} at location!"""

    TELEGRAM_USERNAME_REGEX = '^@[a-z0-9\_]{5,32}$'

    # ALERT
    NORMAL_ALERT = """@{} has just left you a message at http://maps.google.com/?q={},{} ! Travel there to read it :)"""
    ANONYMOUS_ALERT = """Someone has just left you a message at http://maps.google.com/?q={},{} ! Travel there to read it :)"""

    RANDOM_ACTIONS = [
        "You turn over a rock and you find this....\n\n",
        "You look into a tree trunk...! You found something: \n\n",
        "A pigeon plants this letter at your feet... \n\n",
        "You look up and a package gently falls into your lap... \n\n",
        "Etched on a stone, you see... \n\n",
        "You find a letter floating in the wind... \n\n"
    ]

    # ONBOARDING
    ONBOARDING = """Someone has left you a message... send your location to open it!"""
