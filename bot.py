import os
from dataclasses import dataclass
import discord
from discord.ext import commands, tasks


# TODO: figure out dotenv for direnv and type when reading from env var
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]


# Used to track custom updates to settings
@dataclass
class Session:
    is_enabled: bool = False
    sleep_hour: int = 23
    days_of_week: str = "MTWRF"


# Sets up the Bot commands
#   command_prefix: the denoter for what the command starts with for this bot
#   intents: idk
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()


# Event invoked when bot is online
@bot.event
async def on_ready():
    print("Hello! Channel Bedtime bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello! Channel Bedtime bot is ready!")


# Task that is invoked and runs a loop
@tasks.loop(minutes=1, count=2)
async def hello_reminder():
    print("Hello Reminder started")
    if hello_reminder.current_loop == 0:
        print("Hello Reminder run: 1")
        return

    print("Hello Reminder run: 2")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("It has been **1 minute** since you said hello!")
    print("Sent hello reminder")


# Commands that can be typed in chat
@bot.command()
async def hello(ctx):
    hello_reminder.start()
    # TIME IS IN UTC
    # human_readable_time = ctx.message.created_at.strftime("%H:%M:%S")
    # await ctx.send(f"Hello! @ {human_readable_time}")
    await ctx.send("Hello!")
    print("Sent hello")


# TODO: use this command w/ arg for something
@bot.command()
async def bedtime(ctx, arg):
    await ctx.send()

# Running the bot
bot.run(BOT_TOKEN)
