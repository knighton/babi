from panoptes.etc.dicts import v2k_from_k2v
from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.surface.base import SayResult


DaySection = enum('DaySection = MORNING AFTERNOON EVENING NIGHT')


class TimeOfDay(CommonArgument):
    def __init__(self, day_offset, section):
        self.day_offset = day_offset
        assert isinstance(self.day_offset, int)

        self.section = section
        if self.section:
            assert DaySection.is_valid(self.section)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        section = DaySection.to_str[self.section] if self.section else None
        return {
            'type': 'TimeOfDay',
            'day_offset': self.day_offset,
            'section': section,
        }

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        tokens = state.time_of_day_mgr.encode(self.day_offset, self.section)
        return SayResult(tokens=tokens, conjugation=Conjugation.S3,
                         eat_prep=False)


class TimeOfDayManager(object):
    def __init__(self):
        self.section2s = {

            DaySection.AFTERNOON: 'afternoon',
            DaySection.EVENING: 'evening',
            DaySection.NIGHT: 'night',
        }

        self.offset2section2ss = {
            -1: {
                DaySection.MORNING: 'yesterday morning'.split(),
                DaySection.AFTERNOON: 'yesterday afternoon'.split(),
                DaySection.EVENING: 'last evening'.split(),
                DaySection.NIGHT: 'last night'.split(),
            },
            0: {
                DaySection.MORNING: 'this morning'.split(),
                DaySection.AFTERNOON: 'this afternoon'.split(),
                DaySection.EVENING: 'this evening'.split(),
                DaySection.NIGHT: ['tonight'],
            },
            1: {
                DaySection.MORNING: 'tomorrow morning'.split(),
                DaySection.AFTERNOON: 'tomorrow afternoon'.split(),
                DaySection.EVENING: 'tomorrow evening'.split(),
                DaySection.NIGHT: 'tomorrow night'.split(),
            },
        }

        self.s2offset_section = {
            (None, 'tonight'): (0, DaySection.NIGHT),
        }

        self.s2offset = {
            'yesterday': -1,
            'last': -1,
            'this': 0,
            'tomorrow': 1,
            'next': 1,
        }

        self.s2section = v2k_from_k2v(self.section2s)

    def encode(self, day_offset, section_of_day):
        """
        (day offset, section of day) -> list of words
        """
        d = self.offset2section2ss.get(day_offset)
        if not d:
            return None

        return d[section_of_day]

    def sub_decode(self, day, section):
        r = self.s2offset_section.get((day, section))
        if r:
            return [r]

        day_offset = self.s2offset.get(day)
        if not day_offset:
            return []

        section_of_day = self.s2section.get(section)
        if not section_of_day:
            return []

        r = (day_offset, section_of_day)
        return [r]

    def decode(self, first, second):
        """
        (first word, second word) -> (day offset, section of day)
        """
        rr = []

        # Eg, "tomorrow night", "tonight".
        rr += self.sub_decode(first, second)

        # Eg, "tomorrow".
        rr += self.sub_decode(second, None)

        return rr
