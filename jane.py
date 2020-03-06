#!/usr/bin/python3.6
"""" Jane bot by Natasha """
from pprint import pprint
import random
import time
import calendar
import asyncio
import reminder
import grammar
import doggolib
from typing import List, Any
import discord
from discord.ext.commands import Bot

BOT_PREFIX = ('Jane, ', '!jane ', '!j ', '.j ')
TOKEN = 'NDA5NDk5MjI4ODY0NTEyMDEw.DpF2LA.KksfwyYaeZdFeAICRx2TA5QGEOA'

BOT = Bot(command_prefix=BOT_PREFIX)
reminds: List[Any] = []


@BOT.event
async def on_ready():
    """ Prints bot status to console """
    print('Logged in as')
    print(BOT.user.name)
    print(BOT.user.id)


@BOT.command(
    name="clear",
    description='If you ask Jane nicely, she will clear all the mess',
    brief='Let Jane tidy up the chat',
    pass_context=True
)
async def clear(context, amount=100, options='my'):
    """ Deletes many messages in chat... """
    messages = []
    channel = context.message.channel
    role = context.message.author.top_role.name
    async for message in BOT.logs_from(channel, limit=int(amount)):
        if (options == 'every') and (role == 'Terrible DM' or role == 'DANGO SUPER OK!!!'):
            messages.append(message)
        elif message.author == context.message.author:
            messages.append(message)
    await BOT.delete_messages(messages)
    await BOT.say("At your service")


@BOT.command(
    name="remind",
    description='Ask Jane to remind you something. She will remember it - she is quite resourceful girl',
    brief='Let Jane remind you something',
    pass_context=True
)
async def remind(context, target, *, text):
    """ remind @someone to do 'something' at/on 'hh:mm' / in 'number' 'units' """
    text = reminder.format_text(text)

    try:
        remind_time = reminder.parse_time(text)
    except Exception as exception:
        pprint(exception)
        await BOT.say("I think I don`t quite get what you mean.")
        return

    # Generate other information
    author = context.message.author
    channel = context.message.channel
    if target == 'me':
        target = author
    else:
        target = discord.utils.find(lambda m: m.mention == target, context.message.mentions)
    try:
        reminds.append((target, text[0], remind_time, author, channel))
    except Exception as exception:
        pprint(exception)
        await BOT.say("Hold on, please, I am not feeling well right now...")

    print("Remind activated")
    pprint((target, text[0], remind_time, author, channel))
    await BOT.say("Sure thing!")


async def remind_task():
    """ Actual routine checking for reminds """

    await BOT.wait_until_ready()
    while not BOT.is_closed:
        for i, entry in enumerate(reminds):
            if calendar.timegm(reminds[i][2]) <= time.time():
                entry = reminds.pop(i)
                entry = reminder.generate_data(entry)
                data = {'target': entry[0], 'author': entry[2], 'text': entry[1]}
                message = random.choice(reminder.possible_replies).format(**data)
                await BOT.send_message(entry[3], message)
                print("REMIND")
        await asyncio.sleep(3)


@BOT.command(
    name="hi",
    aliases=['hello', 'greetings', 'granko'],
    description='Greet Jane and she should politely reply',
    brief='Greet Jane',
    pass_context=True
)
async def greet(context):
    """ Jane greets you """
    message = context.message
    replies = [
        "Hello {}!".format(message.author.mention),
        "Greetings!",
        "Granko, {}".format(message.author.mention),
        "I am delighted to meet you {}".format(message.author.mention)
    ]
    reply = random.choice(replies)
    await BOT.say(reply)


@BOT.command(
    name="lookup",
    aliases=['define', 'grammar', 'lu'],
    description='Look up a word in a dictionary, (def - definition, phrase - phrases, pv - phrasal verbs)',
    brief='Jane will look up a definition of a word',
    pass_context=False
)
async def lookup(word, opts="def"):
    """ Lookup in dictionary"""
    await BOT.say("Hold on for a second...")
    strings = grammar.serve(word, opts)
    for string in strings:
        await BOT.say(string)


@BOT.command(
    name="doggo",
    aliases=['dog, DOG, doggo, peso, hauko, hafko, havino'],
    description='Retrieves a picture of a dog, '
                '`overtime` option will continuously send dog pictures for 10 minutes'
                '`stop` will stop sending pictures',
    brief='Jane will provide you with a picture of a cute doggo',
    pass_context=True
)
async def doggo(ctx, opts=""):
    """ Get a photo of a cute dog """
    link = doggolib.serve(ctx, opts)
    await  BOT.say(link)


async def doggo_task():
    """ Actual routine checking for doggo jobs """

    await BOT.wait_until_ready()
    while not BOT.is_closed:
        channel, link = doggolib.bg_serve()
        if link != "" and channel is not None:
            await BOT.send_message(channel, link)
        await asyncio.sleep(10)


@BOT.command(
    name="echo",
    aliases=['test', 'say'],
    description='Jane will attempt to repeat what you say',
    brief='Repeat an argument, role restricted',
    pass_context=True
)
async def echo(context, *, txt):
    """ Lookup in dictionary"""
    role = context.message.author.top_role.name
    if role == 'Terrible DM' or role == 'DANGO SUPER OK!!!':
        await  BOT.say(txt)
    else:
        await  BOT.say("I am sorry, but I think that Natasha wouldn`t allow that.")

BOT.loop.create_task(remind_task())
BOT.loop.create_task(doggo_task())
BOT.run(TOKEN)
