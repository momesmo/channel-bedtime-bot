from discord.ext import commands

from utils.flags import BedtimeFlags, SetChannelFlags
from utils.exceptions import ValidationError

class BedtimeCommands(commands.Cog):

    def __init__(self, bot, logger, mongo_client, tasks_cog):
        self.bot = bot
        self.logger = logger
        self.mongo_client = mongo_client
        self.tasks_cog = tasks_cog

    @commands.hybrid_command(name='start', description='Starts bedtime bot')
    async def start(self, ctx):
        """
        A command that starts the bedtime bot.
        """
        # use MongoClient to get sleep_time from guild_settings collection
        guild_settings = self.mongo_client.guild_settings.find_one({"guild_id": ctx.guild.id})
        if not guild_settings or 'sleep_time' not in guild_settings:
            await ctx.send("Sleep time is not set. Please set it first using the \"/bedtime\" command.")
            self.logger.error("Sleep time is not set.")
            return
        if self.tasks_cog.time_check_loop.is_running():
            next_it_time = self.tasks_cog.time_check_loop.next_iteration.astimezone(session.tz).strftime(session.strftime)
            await ctx.send(f"Process is already running. Next execution time is: {next_it_time} {session.time_zone}\n"
                        f"Remaining time: {self.tasks_cog.output_timestamp_remaining(session.sleep_time)}")
        else:
            self.tasks_cog.time_check_loop.start()
            # await bot.change_presence(activity=bot_activity(), status=Status.online)
            session.enabled = True
            await ctx.send("Process has been started.")
            self.logger.info("Process has been started.")


    @commands.hybrid_command(name='stop', description='Stops bedtime bot')
    async def stop(self, ctx):
        """
        Stop the bedtime bot.

        This function stops the bedtime bot by canceling the TimeCheckLoop if it is running.
        If the TimeCheckLoop is not running, it sends a message indicating that the process was not running.
        After canceling the TimeCheckLoop, it sends a message indicating that the process has been canceled and logs the cancellation event.
        """
        if not self.tasks_cog.time_check_loop.is_running():
            await ctx.send("Process was not running.")
        else:
            self.tasks_cog.time_check_loop.cancel()
            # await bot.change_presence(activity=bot_activity(), status=Status.idle)
            await ctx.send("Process has been canceled.")
            self.logger.info("Process has been canceled.")


    @commands.hybrid_command(name='bedtime', description='Sets sleep time for bedtime bot')
    async def bedtime(self, ctx, *, flags: BedtimeFlags):
        """
        Set sleep time for bedtime bot.

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
            self.logger.info("Bedtime set to: %s", session.sleep_time)
            if session.sleep_time < datetime.now().time():
                session.scheduled_in_past = True
                self.logger.info("Bedtime scheduled in past. Setting scheduled_in_past to True.")
            if warning and warning != "Valid input.":
                thread = await session.channel.create_thread(
                    name="Bedtime Warning",
                    auto_archive_duration=60,
                    reason="Providing Bedtime Warning",
                    type=ChannelType.public_thread)
                await thread.send(warning)
            msg_add = ""
            if session.enabled:
                msg_add = f"Process is running. Remaining time: {self.tasks_cog.output_timestamp_remaining(session.sleep_time)}"
            else:
                msg_add = f"Process is not running. Remaining time if started now: {self.tasks_cog.output_timestamp_remaining(session.sleep_time)}"
            await ctx.send(f"Bedtime set to: {session.sleep_time} {session.time_zone}\n"
                        f"{msg_add}")
        except ValidationError as e:
            await ctx.send(f"Bedtime could not be set due to incorrect input: {flags.__dict__}\nError: {e.message}")
            self.logger.error("Bedtime could not be set due to incorrect input: %s. Error: %s", flags.__dict__, e.message)
        except ValueError as e:
            await ctx.send(f"Bedtime could not be set due to incorrect input: {flags.__dict__}\nError: {e}")
            self.logger.error("Bedtime could not be set due to incorrect input: %s. Error: %s", flags.__dict__, e)


    # TODO: finish implementation (not synced to guild since I removed the guild parameters)
    @commands.hybrid_command(name='vote', description='Creates poll for bedtime')
    async def vote(self, ctx):
        """
        Vote for bedtime.

        This function votes for bedtime. It sends a message to the context object indicating that the vote has been received.
        """
        await ctx.send("Vote received.")


    @commands.hybrid_command(name='setchannel', description='Sets the text channel for the bot')
    async def setchannel(self, ctx, *, flags: SetChannelFlags):
        """
        Sets the text channel for the bot.
        """
        await save_channel(ctx.guild.id, flags.channel.id, "Mmmm, cozy. This is my new home.")
        self.logger.info("%s (id=%s): SetChannel %s (id=%s)", ctx.guild.name, ctx.guild.id, flags.channel, flags.channel.id)
        await ctx.send(f"Channel set: {flags.channel.mention}")

    @commands.hybrid_command(name='hello', description='Bot says hello')
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")
