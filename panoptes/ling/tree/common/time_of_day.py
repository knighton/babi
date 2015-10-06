from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.surface.base import SayResult


DayPart = enum('DayPart = MORNING AFTERNOON EVENING NIGHT')


class TimeOfDay(CommonArgument):
    def __init__(self, day_offset, part):
        self.day_offset = day_offset
        assert isinstance(self.day_offset, int)

        self.part = part
        if self.part:
            assert isinstance(self.part, DayPart)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'TimeOfDay',
            'day_offset': self.day_offset,
            'part': DayPart.to_str[self.part] if self.part else None,
        }

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        tokens = []

        day_token = {
            -1: 'yesterday',
            0: 'this',
            +1: 'tomorrow',
        }[self.day_offset]
        tokens.append(day_token)

        if self.part:
            part_token = {
                DayPart.MORNING: 'morning',
                DayPart.AFTERNOON: 'afternoon',
                DayPart.EVENING: 'evening',
                DayPart.NIGHT: 'night',
            }[self.part]
            tokens.append(part_token)

        return SayResult(tokens=tokens, conjugation=Conjugation.S3,
                         eat_prep=False)
