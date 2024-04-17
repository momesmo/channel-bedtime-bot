"""
This module contains the Discord bot.

The bot is implemented using the discord.py library.

This module imports the necessary dependencies and sets up the bot commands.
"""
import os
from datetime import datetime, timedelta
# import json
import random
from collections import defaultdict
import discord
from discord import app_commands
from discord.ext import commands, tasks

from customflags import BedtimeFlags
from customexceptions import ValidationError
from customenums import KillMethod
from session import Session
from logger import Logger
# TODO: figure out pylint in Github Actions failures

# TODO: figure out dotenv for direnv and type when reading from env var
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
GUILD_ID = int(os.environ['GUILD_ID'])
PANTRY_KEY = os.environ['PANTRY_KEY']


# Sets up the Bot commands
#   command_prefix: the denoter for what the command starts with for this bot
#   intents: idk
bot = commands.Bot(command_prefix="!", description="Channel Bedtime Bot", intents=discord.Intents.all())
session = Session()
logger = Logger("bedtime_bot", filename="discord.log", stdout=True)


@bot.event
async def on_ready():
    """
    Event handler that is called when the bot is ready to start receiving events.
    This function sets up the bot's channel, syncs the bot's tree with the guild,
    and sends a welcome message to the channel.

    Parameters:
        None

    Returns:
        None
    """
    session.channel = bot.get_channel(CHANNEL_ID)
    await bot.tree.sync(guild=discord.Object(GUILD_ID))
    await session.channel.send("Hello! Channel Bedtime bot is ready!")
    # embed = discord.Embed(
    #         type="rich",
    #         title="Hello! Channel Bedtime bot is ready!",
    #        description="This bot will help you set your sleep time. "\
    #            "Use the \"/bedtime\" command to set your sleep time and \"/start\" to start the timer.",
    #         color=0x00ff00
    #     )
    # embed.set_author(name="Bedtime Bot", url="https://github.com/momesmo/channel-bedtime-bot")
    # embed.add_field(name="Members", value=len([x for x in bot.get_all_members()]))
    # embed.add_field(name="Channels", value=len([x for x in bot.get_all_channels()]))
    # await session.channel.send(embed=embed)
    logger.info("Channel Bedtime bot initialized.")
# TODO: REMOVE THIS IS FOR TESTING
    await kill_task(KillMethod.ALL)
    # pass

##### POST-MVP #####
# TODO: create stats method to display stats after stop method and kill method, bedtime set, etc. Can make it an Embed
# TODO: add timeout functionality
# TODO: add timeout user from using commands after adding multi-guild and db
# TODO: lock commands to only members in voice channel


# TODO: set interval to be large but it updates to shorter as time gets closer
# TODO: also set the interval based on how close bedtime is on inital start
@tasks.loop(seconds=10)
async def time_check_loop():
    """
    This function is a loop that checks the current time and performs an action when the time matches a specific condition.

    Parameters:
        None

    Returns:
        None
    """
    session.executions += 1
    # TODO: on time pass do something
    now_time = datetime.now().time()
    if session.scheduled_in_past:
        logger.info("TimeCheckLoop: scheduled in past Now: %s Bedtime: %s. Skipping...", now_time, session.sleep_time)
        if now_time <= session.sleep_time:
            logger.info("TimeCheckLoop: no longer scheduled in past. Resetting scheduled_in_past...")
            session.scheduled_in_past = False
    elif now_time >= session.sleep_time:
        await session.channel.send(f"Time to sleep has passed: {session.sleep_time} {session.time_zone}")
        session.scheduled_in_past = True
        # TODO: call KillLoop
        await kill_task(session.kill_method)
        logger.info("TimeCheckLoop: triggered. Time to sleep has passed.")


async def kill_task(kill_type=None):
    """
    A function that handles different kill methods based on the input kill type.
    """
    match kill_type:
        case KillMethod.ALL:
            logger.info("KillLoop: Killing with all method.")
            voice_member_dict = get_all_users_in_active_voice_channels()
            for _, members in voice_member_dict.items():
                for member in members:
                    await disconnect_member(member)
            logger.info("KillLoop: Done!\n%s", dict((k, [x.nick for x in v]) for k, v in voice_member_dict.items()))
        case KillMethod.ALLBUTONE:
            logger.info("KillLoop: Killing with all but one method.")
            voice_member_dict = get_all_users_in_active_voice_channels()
            disconnected_channel_members = {k: random.choice(v) for k, v in voice_member_dict.items() if len(v) > 1}
            for _, member in disconnected_channel_members.items():
                await disconnect_member(member)
            logger.info("KillLoop: Done!\n%s", dict((k, v) for k, v in disconnected_channel_members.items()))
        case KillMethod.TRICKLE:
            logger.info("KillLoop: Killing with trickle method.")

        case KillMethod.HALF:
            logger.info("KillLoop: Killing with half method.")

        case KillMethod.RANDOMAMOUNT:
            logger.info("KillLoop: Killing with random amount method.")

        case KillMethod.RANDOM:
            logger.info("KillLoop: Choosing random kill method.")
            kill_task(KillMethod.random_value())
        case _:
            logger.error("KillLoop: No kill method set. Skipping...")


async def disconnect_member(member):
    """
    Disconnects a member from a voice channel by moving them to None.

    Args:
        member (discord.Member): The member to disconnect.

    Returns:
        None
    """
    await member.move_to(None)


def get_all_users_in_active_voice_channels():
    """
    Returns a dictionary where the keys are the names of active voice channels and the values are lists of members in each channel.

    :return: A defaultdict where the keys are the names of active voice channels and the values are lists of members in each channel.
    :rtype: defaultdict(list)
    """
    channel_users_dict = defaultdict(lambda: [])
    voice_channels = [x for x in bot.get_all_channels() if isinstance(x, discord.VoiceChannel)]
    for channel in voice_channels:
        for member in channel.members:
            channel_users_dict[str(channel)].append(member)
    return channel_users_dict


@time_check_loop.before_loop
async def before_time_check_loop():
    """
    This function is the before loop for the TimeCheckLoop task. 
    It waits until the bot is ready, and sends a message with the starting 
    sleep time and the remaining time before the next check execution.
    """
    logger.info('starting TimeCheckLoop...')
    await bot.wait_until_ready()
    await session.channel.send(f"Starting sleeptime bot: Sleep time set to {session.sleep_time} {session.time_zone}\n"
                               f"Remaining time: {output_timestamp_remaining()}")


@time_check_loop.after_loop
async def after_time_check_loop():
    """
    This function is an after loop function for the TimeCheckLoop task. It sends a message with the statistics of the loop execution.

    Parameters:
        None

    Returns:
        None
    """
    logger.info('Post TimeCheckLoop stats...')
    await session.channel.send(f"Stats:\nCheck Executions: {session.executions}\nKills: {session.kills}")


# Before loop helpers
def time_seconds(t):
    """
    A function to calculate the total number of seconds represented by the input time object.
    
    Parameters:
        t: A time object containing hour, minute, and second components.
        
    Returns:
        An integer representing the total number of seconds.
    """
    return (t.hour * 60) + (t.minute * 60) + t.second


def seconds_remaining():
    """
    A function to calculate the total number of seconds remaining until the sleep time.
    """
    now_time_secs = time_seconds(datetime.now().time())
    sleep_time_secs = time_seconds(session.sleep_time)
    if now_time_secs > sleep_time_secs:
        return sleep_time_secs - now_time_secs + (24 * 60 * 60)
    return sleep_time_secs - now_time_secs


def output_timestamp_remaining():
    """
    A function to calculate the remaining time in seconds until the sleep time based on the current time.
    """
    return timedelta(seconds=seconds_remaining())
########


@bot.hybrid_command(name='start', description='Start bedtime bot')
@app_commands.guilds(discord.Object(GUILD_ID))
async def start(ctx):
    """
    A command that starts the bedtime bot.

    Parameters:
        ctx (Context): The context object representing the invocation context.

    Returns:
        None
    """
    if not hasattr(session, 'sleep_time'):
        await ctx.send("Sleep time is not set. Please set it first using the \"/bedtime\" command.")
        logger.error("Sleep time is not set.")
        return
    if time_check_loop.is_running():
        next_it_time = time_check_loop.next_iteration.astimezone(session.tz).strftime(session.strftime)
        await ctx.send(f"Process is already running. Next execution time is: {next_it_time} {session.time_zone}\n"
                       f"Remaining time: {output_timestamp_remaining()}")
    else:
        time_check_loop.start()
        session.enabled = True
        await ctx.send("Process has been started.")
        logger.info("Process has been started.")


@bot.hybrid_command(name='stop', description='Stop bedtime bot')
@app_commands.guilds(discord.Object(GUILD_ID))
async def stop(ctx):
    """
    Stop the bedtime bot.

    Args:
        ctx (Context): The context object representing the invocation context.

    Returns:
        None

    This function stops the bedtime bot by canceling the TimeCheckLoop if it is running.
    If the TimeCheckLoop is not running, it sends a message indicating that the process was not running.
    After canceling the TimeCheckLoop, it sends a message indicating that the process has been canceled and logs the cancellation event.
    """
    if not time_check_loop.is_running():
        await ctx.send("Process was not running.")
    else:
        time_check_loop.cancel()
        await ctx.send("Process has been canceled.")
        logger.info("Process has been canceled.")


@bot.hybrid_command(name='bedtime', description='Set sleep time for bedtime bot')
@app_commands.guilds(discord.Object(GUILD_ID))
async def bedtime(ctx, *, flags: BedtimeFlags):
    """
    Set sleep time for bedtime bot.

    Parameters:
        ctx (Context): The context object representing the invocation context.
        flags (BedtimeFlags): The flags object representing the bedtime flags.

    Returns:
        None

    This function sets the sleep time for the bedtime bot. It takes in the context object and the bedtime flags object as parameters.
    It first validates the parameters using the `validate_params` method of the `flags` object.
    If the parameters are valid, it sets the sleep time using the `get_time` method of the `flags` object.
    It then logs the bedtime set and checks if it is scheduled in the past. If it is, it sets the `scheduled_in_past` flag to True.
    If a warning is provided, it creates a thread with the name "Bedtime Warning" and sends the warning message.
    It then checks if the bot is enabled or not and constructs a message accordingly.
    Finally, it sends the bedtime set message and the additional message to the context object.
    If any validation error occurs, it sends an error message with the input and error details.
    If any other value error occurs, it sends an error message with the input and error details.
    """
    try:
        warning = flags.validate_params()
        session.sleep_time = flags.get_time()
        logger.info("Bedtime set to: %s", session.sleep_time)
        if session.sleep_time < datetime.now().time():
            session.scheduled_in_past = True
            logger.info("Bedtime scheduled in past. Setting scheduled_in_past to True.")
        if warning and warning != "Valid input.":
            thread = await session.channel.create_thread(
                name="Bedtime Warning",
                auto_archive_duration=60,
                reason="Providing Bedtime Warning",
                type=discord.ChannelType.public_thread)
            await thread.send(warning)
        msg_add = ""
        if session.enabled:
            msg_add = f"Process is running. Remaining time: {output_timestamp_remaining()}"
        else:
            msg_add = f"Process is not running. Remaining time if started now: {output_timestamp_remaining()}"
        await ctx.send(f"Bedtime set to: {session.sleep_time} {session.time_zone}\n"
                       f"{msg_add}")
    except ValidationError as e:
        await ctx.send(f"Bedtime could not be set due to incorrect input: {flags.__dict__}\nError: {e.message}")
        logger.error("Bedtime could not be set due to incorrect input: %s. Error: %s", flags.__dict__, e.message)
    except ValueError as e:
        await ctx.send(f"Bedtime could not be set due to incorrect input: {flags.__dict__}\nError: {e}")
        logger.error("Bedtime could not be set due to incorrect input: %s. Error: %s", flags.__dict__, e)

if __name__ == "__main__":
    # Running the bot
    logger.info("Starting bot run...")
    bot.run(BOT_TOKEN)
