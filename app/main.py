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
from discord import app_commands, Intents, Object as DiscordObject, Embed, VoiceChannel, ChannelType, Game, Status, utils as discord_utils
from discord.ext.commands import Bot

from bot.cogs.commands import BedtimeCommands
from bot.cogs.tasks import BedtimeTasks
from config.settings import Settings
from utils.flags import BedtimeFlags, SetChannelFlags
from utils.exceptions import ValidationError
from utils.enums import KillMethod
from utils.session import Session
from utils.logger import Logger
from db.mongo_client import MongoClient

# TODO: figure out pylint in Github Actions failures

# Reference: https://www.youtube.com/@richardschwabe/videos

# Sets up the Bot commands
#   command_prefix: the denoter for what the command starts with for this bot
#   intents: idk
logger = Logger("bedtime_bot",
                filename=Settings.LOG_FILE,
                level=Settings.LOG_LEVEL,
                stdout=True)
bot = Bot(command_prefix="!",
          description="Channel Bedtime Bot",
          intents=Intents.all())

try:
    mongo_client = MongoClient(host=Settings.MONGO_HOST,
                               port=Settings.MONGO_PORT,
                               username=Settings.MONGO_USERNAME,
                               password=Settings.MONGO_PASSWORD,
                               db=Settings.MONGO_DB)
    print(f"MongoDB connected. Server Info: {mongo_client.client.server_info()}")
except Exception as e:
    logger.error("Error connecting to MongoDB: %s", e)
    logger.error("Exiting...")
    exit(1)

tasks_cog = BedtimeTasks(bot, logger, mongo_client)
commands_cog = BedtimeCommands(bot, logger, mongo_client, tasks_cog)
bot.add_cog(commands_cog)
bot.add_cog(tasks_cog)

# TODO: remove all session stuff
session = Session()


def bot_activity():
    return Game(name="https://github.com/momesmo/channel-bedtime-bot",
                type=1, url="https://github.com/momesmo/channel-bedtime-bot")

@bot.event
async def on_guild_join(guild):
    logger.info("%s (id=%s): bot joined guild", guild.name, guild.id)
    guild_settings_id = mongo_client.update_guild_settings(
        guild_id=guild.id,
        data={
            "sleep_time": None,
            "channel_id": None,
            "enabled": False,
            "triggered": False,
            "kill_method": KillMethod.ALL.value,
            "executions": 0,
            "kills": 0
        }
    )
    guild_id = mongo_client.update_guild(
        guild_id=guild.id,
        data={'name': guild.name, 'guild_settings_id': guild_settings_id}
    )
    logger.info("%s (id=%s): Created Mongo Guild Id=%s, Mongo Guild Settings Id=%s",
                guild.name, guild.id, guild_id, guild_settings_id)
    # Bot Message to Channel
    system_channel = guild.system_channel
    if system_channel:
        await save_channel(guild.id, system_channel.id, f"Hello! {bot.user} has joined {guild.name}!")
    else:
        general_channel = discord_utils.get(guild.text_channels, name='general')
        if general_channel is not None:
            await save_channel(guild.id, general_channel.id, f"Hello! {bot.user} has joined {guild.name}!")
        else:
            logger.warning("%s (id=%s): No general/system channel found", guild.name, guild.id)


@bot.event
async def on_guild_remove(guild):
    logger.info("%s (id=%s): bot left guild", guild.name, guild.id)
    guild_delete = mongo_client.delete_guild(guild_id=guild.id)
    guild_settings_delete = mongo_client.delete_guild_settings(guild_id=guild.id)
    logger.info("%s (id=%s): Mongo Guild Delete=%s (%s), Mongo Guild Settings Delete=%s (%s)",
                guild.name, guild.id, guild_delete.deleted_count, guild_delete.acknowledged,
                guild_settings_delete.deleted_count, guild_settings_delete.acknowledged)


@bot.event
async def on_connect():
    logger.info("Bot connected to Discord.")

@bot.event
async def on_ready():
    """
    Event handler that is called when the bot is ready to start receiving events.
    This function sets up the bot's channel, syncs the bot's tree with the guild,
    and sends a welcome message to the channel.
    """
    # TODO: remove session.channel messages
    # session.channel = bot.get_channel(CHANNEL_ID)
    logger.info("Channel Bedtime bot initialized. User: %s (Id: %s)", bot.user.name, bot.user.id)
    synced = await bot.tree.sync()
    logger.info(f"Synced {len(synced)} commands: {", ".join([command.name for command in synced])}")
    await bot.change_presence(activity=bot_activity(), status=Status.idle)
    # await session.channel.send(f"Hello! {bot.user} is now running!")
    '''
    TODO: Embedded message, still testing
    # embed = Embed(
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
    '''
    guilds_str = ", ".join([f"{guild.name} (Id: {guild.id})" for guild in bot.guilds])
    logger.info(f"Connected to {len(bot.guilds)} Servers: {guilds_str}")
# TODO: REMOVE THIS IS FOR TESTING
    # await kill_task(KillMethod.ALL)
    # pass

async def kill_task(kill_type=None):
    """
    A function that handles different kill methods based on the input kill type.
    """
    match kill_type:
        case KillMethod.ALL.value:
            logger.info("KillLoop: Killing with all method.")
            voice_member_dict = get_all_users_in_active_voice_channels()
            for _, members in voice_member_dict.items():
                for member in members:
                    await disconnect_member(member)
            logger.info("KillLoop: Done!\n%s", dict((k, [x.nick for x in v]) for k, v in voice_member_dict.items()))
        case KillMethod.ALLBUTONE.value:
            logger.info("KillLoop: Killing with all but one method.")
            voice_member_dict = get_all_users_in_active_voice_channels()
            disconnected_channel_members = {k: random.choice(v) for k, v in voice_member_dict.items() if len(v) > 1}
            for _, member in disconnected_channel_members.items():
                await disconnect_member(member)
            logger.info("KillLoop: Done!\n%s", dict((k, v) for k, v in disconnected_channel_members.items()))
        case KillMethod.TRICKLE.value:
            logger.info("KillLoop: Killing with trickle method.")

        case KillMethod.HALF.value:
            logger.info("KillLoop: Killing with half method.")

        case KillMethod.RANDOMAMOUNT.value:
            logger.info("KillLoop: Killing with random amount method.")

        case KillMethod.RANDOM.value:
            logger.info("KillLoop: Choosing random kill method.")
            kill_task(KillMethod.random_value())
        case _:
            logger.error("KillLoop: No kill method set. Skipping...")


async def disconnect_member(member):
    """
    Disconnects a member from a voice channel by moving them to None.
    """
    await member.move_to(None)


def get_all_users_in_active_voice_channels():
    """
    Returns a dictionary where the keys are the names of active voice channels and the values are lists of members in each channel.
    """
    channel_users_dict = defaultdict(lambda: [])
    voice_channels = [x for x in bot.get_all_channels() if isinstance(x, VoiceChannel)]
    for channel in voice_channels:
        for member in channel.members:
            channel_users_dict[str(channel)].append(member)
    return channel_users_dict


async def save_channel(guild_id, channel_id=None, message=None):
    """
    Saves the channel id to the guild settings.
    """
    if channel_id:
        mongo_client.update_guild_settings(guild_id=guild_id, data={'channel_id': channel_id})
    if message:
        await bot.get_channel(channel_id).send(message)


async def send_message(message, guild_id=None, channel_id=None):
    if channel_id:
        await bot.get_channel(channel_id).send(message)
    elif guild_id:
        channel_id = mongo_client.get_guild_settings(guild_id=guild_id).get('channel_id', None)
        if channel_id:
            await bot.get_channel(channel_id).send(message)
        else:
            logger.error("Guild id=%s: No channel id found. Skipping message...", guild_id)
    else:
        logger.error("No channel id or guild id provided. Skipping message...")


if __name__ == "__main__":
    # Running the bot
    logger.info("Starting bot run...")
    bot.run(Settings.BOT_TOKEN)
