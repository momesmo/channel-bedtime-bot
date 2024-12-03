from discord.ext import tasks, commands
from datetime import datetime, timedelta

class BedtimeTasks(commands.Cog):
    def __init__(self, bot, logger, mongo_client):
        self.bot = bot
        self.logger = logger
        self.mongo_client = mongo_client

    def cog_unload(self):
        self.time_check_loop.cancel()

    ##### POST-MVP #####
    # TODO: create stats method to display stats after stop method and kill method, bedtime set, etc. Can make it an Embed
    # TODO: add timeout functionality
    # TODO: add timeout user from using commands after adding multi-guild and db
    # TODO: lock commands to only members in voice channel


    # TODO: set interval to be large but it updates to shorter as time gets closer
    # TODO: also set the interval based on how close bedtime is on initial start
    @tasks.loop(seconds=10)
    async def time_check_loop(self):
        """
        This function is a loop that checks the current time and performs an action when the time matches a specific condition.
        """
        session.executions += 1
        now_time = datetime.now().time()
        if session.scheduled_in_past:
            self.logger.info("TimeCheckLoop: scheduled in past Now: %s Bedtime: %s. Skipping...", now_time, session.sleep_time)
            if now_time <= session.sleep_time:
                self.logger.info("TimeCheckLoop: no longer scheduled in past. Resetting scheduled_in_past...")
                session.scheduled_in_past = False
        elif now_time >= session.sleep_time:
            await session.channel.send(f"Time to sleep has passed: {session.sleep_time} {session.time_zone}")
            session.scheduled_in_past = True
            await kill_task(session.kill_method)
            self.logger.info("TimeCheckLoop: triggered. Time to sleep has passed.")

    @time_check_loop.before_loop
    async def before_time_check_loop():
        """
        This function is the before loop for the TimeCheckLoop task. 
        It waits until the bot is ready, and sends a message with the starting 
        sleep time and the remaining time before the next check execution.
        """
        self.logger.info('starting TimeCheckLoop...')
        await self.bot.wait_until_ready()
        await session.channel.send(f"Starting sleeptime bot: Sleep time set to {session.sleep_time} {session.time_zone}\n"
                                f"Remaining time: {BedtimeTasks.output_timestamp_remaining()}")

    @time_check_loop.after_loop
    async def after_time_check_loop():
        """
        This function is an after loop function for the TimeCheckLoop task. It sends a message with the statistics of the loop execution.

        """
        self.logger.info('Post TimeCheckLoop stats...')
        await session.channel.send(f"Stats:\nCheck Executions: {session.executions}\nKills: {session.kills}")

    # Before loop utils
    @staticmethod
    def time_seconds(t):
        """
        A function to calculate the total number of seconds represented by the input time object.
        """
        return (t.hour * 60) + (t.minute * 60) + t.second


    @staticmethod
    def seconds_remaining(sleep_time):
        """
        A function to calculate the total number of seconds remaining until the sleep time.
        """
        now_time_secs = BedtimeTasks.time_seconds(datetime.now().time())
        sleep_time_secs = BedtimeTasks.time_seconds(sleep_time)
        if now_time_secs > sleep_time_secs:
            return sleep_time_secs - now_time_secs + (24 * 60 * 60)
        return sleep_time_secs - now_time_secs


    @staticmethod
    def output_timestamp_remaining(sleep_time):
        """
        A function to calculate the remaining time in seconds until the sleep time based on the current time.
        """
        return timedelta(seconds=BedtimeTasks.seconds_remaining(sleep_time))