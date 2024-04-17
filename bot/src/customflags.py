"""
This module contains the custom flag class.
"""
from datetime import datetime
from discord.ext import commands
from customexceptions import ValidationError


class BedtimeFlags(commands.FlagConverter):
    """
    The custom bedtime command flags.
    """
    time_str: str = commands.flag(default="", description="Time in 24 hour format. E.g. 23:00:00 or 23:00")
    hour: int = commands.flag(default=0, description="Hour")
    minute: int = commands.flag(default=0, description="Minute")
    second: int = commands.flag(default=0, description="Second")

    def validate_params(self):
        """
        Validates the parameters passed to the flag.
        """
        if not self.time_str and self.hour == 0:
            raise ValidationError("Invalid input. Must provide time in format 23:00:00 or 23:00 or hour parameters (minute and second defaults to 0)")
        if self.time_str and (self.hour != 0 or self.minute != 0 or self.second != 0):
            return "Warning: Provided time_str overrides hour, minute, second parameters."

    def get_time(self):
        """
        Returns the time in datetime.time format from params.
        """
        params = self.__dict__
        str_time = params.get("time_str") or f"{params.get('hour')}:{params.get('minute')}:{params.get('second')}"
        if str_time.count(':') == 1:
            str_time += ':00'
        return datetime.strptime(str_time, '%H:%M:%S').time()
