from enum import Enum
import random


class KillMethod(Enum):
    ALL = "all"
    ALLBUTONE = "all_but_one"
    TRICKLE = "trickle"
    HALF = "half"
    RANDOMAMOUNT = "random_amount"
    RANDOM = "random"

    @classmethod
    def random_value(cls):
        return random.choice(cls._all_but_random())

    @classmethod
    def _all_but_random(cls):
        return [x for x in list(cls) if x != cls.RANDOM]
