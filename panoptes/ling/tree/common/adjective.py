from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.surface.base import SayResult


class Adjective(CommonArgument):
    def __init__(self, s):
        self.s = s
        assert self.s
        assert isinstance(self.s, basestring)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': self.__class__.__name__,
            's': self.s,
        }

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        return SayResult(tokens=[self.s], conjugation=S3, eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(self, d, loader):
        return Adjective(d[s])
