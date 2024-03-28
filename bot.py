import os
from datetime import datetime, timedelta
import discord
from discord import app_commands
from discord.ext import commands, tasks

from customflags import BedtimeFlags
from customexceptions import ValidationError
from customenums import KillMethod
from session import Session
from logger import Logger
# TODO: figure out pylint in Github Actions failures
# TODO: VSCode warning: You are connected toan OS version that is unsupported by VSCode

# TODO: figure out dotenv for direnv and type when reading from env var
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
GUILD_ID = int(os.environ['GUILD_ID'])


# Sets up the Bot commands
#   command_prefix: the denoter for what the command starts with for this bot
#   intents: idk
bot = commands.Bot(command_prefix="!", description="Bedtime Bot", intents=discord.Intents.all())
session = Session()
logger = Logger("bedtime_bot", "discord.log", stdout=True)


@bot.event
async def on_ready():
    session.channel = bot.get_channel(CHANNEL_ID)
    await bot.tree.sync(guild=discord.Object(GUILD_ID))
    await session.channel.send("Hello! Channel Bedtime bot is ready!")
    # embed = discord.Embed(
    #         type="rich",
    #         title="Hello! Channel Bedtime bot is ready!",
    #         description="This bot will help you set your sleep time. Use the \"/bedtime\" command to set your sleep time and \"/start\" to start the timer.",
    #         color=0x00ff00
    #     )
    # embed.set_author(name="Bedtime Bot", url="https://github.com/momesmo/channel-bedtime-bot")
    # embed.add_field(name="Members", value=len([x for x in bot.get_all_members()]))
    # embed.add_field(name="Channels", value=len([x for x in bot.get_all_channels()]))
    # await session.channel.send(embed=embed)
    logger.info("Channel Bedtime bot initialized.")


# TODO: set interval to be large but it updates to shorter as time gets closer
# TODO: also set the interval based on how close bedtime is on inital start
@tasks.loop(seconds=10)
async def TimeCheckLoop():
    session.executions += 1
    # TODO: on time pass do something
    now_time = datetime.now().time()
    if session.scheduled_in_past:
        logger.info(f"TimeCheckLoop: scheduled in past Now: {now_time} Sleep: {session.sleep_time}. Skipping...")
        if now_time <= session.sleep_time:
            logger.info("TimeCheckLoop: no longer scheduled in past. Resetting scheduled_in_past...")
            session.scheduled_in_past = False
    elif now_time >= session.sleep_time:
        await session.channel.send(f"Time to sleep has passed: {session.sleep_time} {session.time_zone}")
        session.scheduled_in_past = True
        # TODO: call KillLoop
        logger.info("TimeCheckLoop: triggered. Time to sleep has passed.")


async def kill_task(kill_type=None):
    match kill_type:
        case KillMethod.ALL:
            await session.channel.send("KillLoop: Killing with all method.")
        case KillMethod.ALLBUTONE:
            await session.channel.send("KillLoop: Killing with all but one method.")
        case KillMethod.TRICKLE:
            await session.channel.send("KillLoop: Killing with trickle method.")
        case KillMethod.RANDOM:
            await session.channel.send("KillLoop: Choosing random kill method.")
            kill_task(KillMethod.random_value())
        case _:
            await session.channel.send("ERROR: KillLoop: No kill method set. Skipping...")
            logger.error("KillLoop: No kill method set. Skipping...")


@TimeCheckLoop.before_loop
async def before_TimeCheckLoop():
    logger.info('starting TimeCheckLoop...')
    await bot.wait_until_ready()
    await session.channel.send(f"Starting sleeptime bot: Sleep time set to {session.sleep_time} {session.time_zone}\n"
                               f"Remaining time: {timedelta(seconds=seconds_remaining())}")


@TimeCheckLoop.after_loop
async def after_TimeCheckLoop():
    logger.info('Post TimeCheckLoop stats...')
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


@bot.hybrid_command(name='start', description='Start bedtime bot')
@app_commands.guilds(discord.Object(GUILD_ID))
async def start(ctx):
    if not hasattr(session, 'sleep_time'):
        await ctx.send("Sleep time is not set. Please set it first using the \"/bedtime\" command.")
        logger.error("Sleep time is not set.")
        return
    if TimeCheckLoop.is_running():
        next_it_time = TimeCheckLoop.next_iteration.astimezone(session.tz).strftime(session.strftime)
        await ctx.send(f"Process is already running. Next execution time is: {next_it_time} {session.time_zone}")
    else:
        TimeCheckLoop.start()
        session.enabled = True
        await ctx.send("Process has been started.")
        logger.info("Process has been started.")


@bot.hybrid_command(name='stop', description='Stop bedtime bot')
@app_commands.guilds(discord.Object(GUILD_ID))
async def stop(ctx):
    if not TimeCheckLoop.is_running():
        await ctx.send("Process was not running.")
    else:
        TimeCheckLoop.cancel()
        await ctx.send("Process has been canceled.")
        logger.info("Process has been canceled.")


@bot.hybrid_command(name='bedtime', description='Set sleep time for bedtime bot')
@app_commands.guilds(discord.Object(GUILD_ID))
async def bedtime(ctx, *, flags: BedtimeFlags):
    try:
        warning = flags.validate_params()
        session.sleep_time = flags.get_time()
        logger.info(f"Bedtime set to: {session.sleep_time}")
        if session.sleep_time < datetime.now().time():
            session.scheduled_in_past = True
            logger.info("Bedtime scheduled in past. Setting scheduled_in_past to True.")
        if warning:
            thread = await session.channel.create_thread(
                name="Bedtime Warning",
                auto_archive_duration=60,
                reason="Providing Bedtime Warning",
                type=discord.ChannelType.public_thread)
            await thread.send(warning)
        await ctx.send(f"Bedtime set to: {session.sleep_time} {session.time_zone}")
    except ValidationError as e:
        await ctx.send(f"Bedtime could not be set due to incorrect input: {flags.__dict__}\nError: {e.message}")
        logger.error("Bedtime could not be set due to incorrect input: %s. Error: %s" % (flags.__dict__, e.message))
    except ValueError as e:
        await ctx.send(f"Bedtime could not be set due to incorrect input: {flags.__dict__}\nError: {e}")
        logger.error("Bedtime could not be set due to incorrect input: %s. Error: %s" % (flags.__dict__, e))


# Running the bot
logger.info("Starting bot run...")
bot.run(BOT_TOKEN)
