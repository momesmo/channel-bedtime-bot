import os
from dataclasses import dataclass
from datetime import time, datetime, timedelta
import discord
from discord.ext import commands, tasks
from customexceptions import ValidationError
# TODO: figure out pylint in Github Actions failures
# TODO: VSCode warning: You are connected toan OS version that is unsupported by VSCode

# TODO: figure out dotenv for direnv and type when reading from env var
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])


# Used to track custom updates to settings
@dataclass
class Session:
    channel: object = None
    enabled: bool = False
    triggered: bool = False
    # sleep_hour: int = 23
    trigger_dow: str = "MTWRF"  # TODO: implement command & logic for this
    sleep_time: time = time(0, 0, 0)
    time_zone: str = ""
    tz: object = None
    executions: int = 0
    kills: int = 0
    strftime: str = "%Y-%m-%d %H:%M:%S"


# Sets up the Bot commands
#   command_prefix: the denoter for what the command starts with for this bot
#   intents: idk
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()


# Event invoked when bot is online
@bot.event
async def on_ready():
    print("Hello! Channel Bedtime bot is ready!")
    session.channel = bot.get_channel(CHANNEL_ID)
    await session.channel.send("Hello! Channel Bedtime bot is ready!")


# Task that is invoked and runs a loop
@tasks.loop(seconds=30, count=2)
async def hello_reminder():
    print("Hello Reminder started")
    if hello_reminder.current_loop == 0:
        print("Hello Reminder run: 1")
        return

    print("Hello Reminder run: 2")
    await session.channel.send("It has been **1 minute** since you said hello!")
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


# TODO: set interval to be large but it updates to shorter as time gets closer
# TODO: also set the interval based on how close bedtime is on inital start
@tasks.loop(minutes=1)
async def TimeCheckLoop():
    session.executions += 1
    # TODO: on time pass do something
    now_time = datetime.now().time()
    if now_time >= session.sleep_time:
        await session.channel.send(f"Time to sleep has passed: {session.sleep_time} {session.time_zone}")
        TimeCheckLoop.stop()


@TimeCheckLoop.before_loop
async def before_TimeCheckLoop():
    print('starting TimeCheckLoop...')
    await bot.wait_until_ready()
    await session.channel.send(f"""Starting sleeptime bot: Sleep time set to {session.sleep_time} {session.time_zone}\n
                               Remaining time: {timedelta(seconds=seconds_remaining())}""")


@TimeCheckLoop.after_loop
async def after_TimeCheckLoop():
    print('stopping TimeCheckLoop...')
    await session.channel.send(f"Stats:\nCheck Executions: {session.executions}\nKills: {session.kills}")


# Before loop helpers
def seconds_remaining():
    now_time_secs = time_seconds(datetime.now().time())
    sleep_time_secs = time_seconds(session.sleep_time)
    if now_time_secs > sleep_time_secs:
        return sleep_time_secs - now_time_secs + (24 * 60 * 60)
    return sleep_time_secs - now_time_secs


def time_seconds(t):
    return (t.hour * 60) + (t.minute * 60) + t.second
########


@bot.command()
async def start(ctx):
    if TimeCheckLoop.is_running():
        next_it_time = TimeCheckLoop.next_iteration.astimezone(session.tz).strftime(session.strftime)
        await ctx.send(f"Process has already started. Next execution time is: {next_it_time} {session.time_zone}")
    else:
        TimeCheckLoop.start()
        session.enabled = True


@bot.command()
async def stop(ctx):
    TimeCheckLoop.cancel()


@bot.command()
async def bedtime(ctx, arg):
    try:
        session.sleep_time = str_to_time(arg)
        session.time_zone = session.time_zone or time_zone()
        await ctx.send(f"Bedtime set to: {session.sleep_time} {session.time_zone}")
    except ValidationError as e:
        await ctx.send(f"Bedtime could not be set due to incorrect input: {arg}\nError: {e.message}")


def str_to_time(str_time):
    time_arr = []
    for i in str_time.split(':'):
        time_arr.append(int(i))

    if len(time_arr) == 2:
        return time(hour=time_arr[0], minute=time_arr[1])
    elif len(time_arr) == 3:
        return time(hour=time_arr[0], minute=time_arr[1], second=time_arr[2])
    else:
        raise ValidationError("Time format is incorrect. Acceptable formats: %H:%M or %H:%M:%S (24 hour format only)")


def time_zone():
    local = datetime.now().astimezone()
    session.tz = local.tzinfo
    return session.tz.tzname(local)


# Running the bot
bot.run(BOT_TOKEN)
