"""
This module contains the custom enum class.
"""
from enum import Enum
import random


class KillMethod(Enum):
    """
    The enum class for the kill method.
    """
    ALL = "all"
    ALLBUTONE = "all_but_one"
    TRICKLE = "trickle"
    HALF = "half"
    RANDOMAMOUNT = "random_amount"
    RANDOM = "random"

    @classmethod
    def random_value(cls):
        """
        Generate a random value from the class.

        Returns:
            The randomly chosen value from the class.
        """
        return random.choice(cls._all_but_random())

    @classmethod
    def _all_but_random(cls):
        """
        Returns a list of all enum members except for the RANDOM member.

        :return: A list of enum members.
        :rtype: list
        """
        return [x for x in list(cls) if x != cls.RANDOM]
