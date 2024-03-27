from dataclasses import dataclass
from datetime import time, datetime

from customenums import KillMethod


@dataclass
class Session:
    time_zone: str
    sleep_time: time
    scheduled_in_past: bool = False
    channel: object = None
    enabled: bool = False
    triggered: bool = False
    # sleep_hour: int = 23
    trigger_dow: str = "MTWRF"  # TODO: implement command & logic for this
    tz: object = None
    kill_method: KillMethod = KillMethod.All
    executions: int = 0
    kills: int = 0
    strftime: str = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.time_zone = self.get_time_zone()

    def get_time_zone(self):
        local = datetime.now().astimezone()
        self.tz = local.tzinfo
        return self.tz.tzname(local)
