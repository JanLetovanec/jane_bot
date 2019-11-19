""" Helper library for remind function """
import requests


overtime_activated = False
flood_channel = None


def get_img():
    r = requests.get("https://dog.ceo/api/breeds/image/random").json()
    return r["message"]


"""
API 
"""


def serve(ctx, options):
    global overtime_activated
    global flood_channel

    if options == "overtime":
        overtime_activated = True
        flood_channel = ctx.message.channel
        print("Doggo - Overtime activated")
        return "As you wish."
    elif options == "stop":
        print("Doggo - Overtime deactivated")
        overtime_activated = False
    else:
        return get_img()


def bg_serve():
    if overtime_activated:
        return flood_channel, get_img()
    return None, ""
