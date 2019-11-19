""" Helper library for remind function """
from pprint import pprint
import time

possible_replies = [
    "Hi {target}, sorry to interupt you, but {author} wanted me to remind you: {text}",
    "{target}! {author} wanted me to tell you this: {text}",
    "{target}, hope I am not interupting you, but : {text} . Just thought you might like to know."
]


def format_text(text):
    """ Formats the string to reasonable and uniform way """
    text = text.replace('to do ', '') \
        .replace('to ', '') \
        .replace(' at ', ' on ') \
        .replace(' a ', ' 1 ') \
        .replace(' an ', ' 1 ') \
        .replace('minutes', '60') \
        .replace('minute', '60') \
        .replace('seconds', '1') \
        .replace('second', '1') \
        .replace('hours', '3600') \
        .replace('hour', '3600')
    text = text.split(' ')
    pure_text = ""
    if text[-3] == 'in':
        for i in range(0, (len(text)-3)):
            pure_text += " " + text[i]
        final_text = [pure_text, text[-3], text[-2], text[-1]]
    else:
        for i in range(0, (len(text)-2)):
            pure_text += text[i]
        final_text = [pure_text, text[-2], text[-1]]
    if len(text) < 3:
        pprint(final_text)
        raise Exception("Bad remind request")

    return final_text


def parse_time(text):
    """ Tries to parse the time as written by user"""

    # When keyword is 'in' adds values to time
    if text[-3] == 'in':
        remind_time = time.gmtime(int(text[-2]) * int(text[-1]) + time.time())
    # Otherwise try to parse time as written
    else:
        remind_time = text[-1].replace(':', ' ') \
                    + " " \
                    + time.strftime("%m/%d/%y", time.gmtime(time.time()))
        remind_time = time.strptime(remind_time, "%H %M %m/%d/%y")
    return remind_time


def generate_data(entry):
    target = entry[0]
    text = entry[1]
    author = entry[3]
    channel = entry[4]
    if target == author:
        author = 'you'
        target = target.mention
    else:
        author = author.name
        target = target.mention
    return target, text, author, channel
