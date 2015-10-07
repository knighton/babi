from panoptes.ling.tree.common.time_of_day import DaySection
from panoptes.mind.idea.base import Idea


class RelativeDay(Idea):
    def __init__(self, day_offset, section):
        self.day_offset = day_offset
        assert isinstance(self.day_offset, int)

        self.section = section
        if self.section:
            assert DaySection.is_valid(self.section)

    def dump(self):
        section = DaySection.to_str[self.section] if self.section else None
        return {
            'type': 'RelativeDay',
            'day_offset': self.day_offset,
            'section': section,
        }

    def to_time_span(self):
        a = self.day_offset * len(DaySection.values)
        if self.section:
            a += self.section - DaySection.first
            z = a
        else:
            z = a + len(DaySection.values) - 1
        return a, z
