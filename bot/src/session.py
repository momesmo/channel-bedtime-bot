"""
This module contains the session class that stores the state of the bot.
"""
from dataclasses import dataclass
from datetime import time, datetime, timezone

from customenums import KillMethod


@dataclass
class Session:
    """
    Dataclass that stores the state of the bot.
    """
    time_zone: str
    sleep_time: time
    scheduled_in_past: bool = False
    channel: object = None
    enabled: bool = False
    triggered: bool = False
    # sleep_hour: int = 23
    trigger_dow: str = "MTWRF"  # TODO: implement command & logic for this
    tz: timezone = None
    kill_method: KillMethod = KillMethod.ALL
    executions: int = 0
    kills: int = 0
    strftime: str = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        """
        Initializes the session object.
        """
        self.time_zone = self.get_time_zone()

    def get_time_zone(self):
        """
        Returns the time zone of the session.
        """
        local = datetime.now().astimezone()
        self.tz = local.tzinfo
        return self.tz.tzname(local)
