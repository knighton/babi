from ling.glue.inflection import Conjugation
from ling.glue.magic_token import POSSESSIVE_MARK
from ling.tree.common.base import *


class ProperNoun(Argument):
    """
    A simple proper noun.
    """

    def __init__(self, name, is_plur):
        self.name = name
        assert isinstance(self.name, tuple)
        for s in self.name:
            assert isinstance(s, basestring)

        self.is_plur = is_plur
        assert isinstance(self.is_plur, bool)

    def decide_conjugation(self):
        if self.is_plur:
            return Conjugation.P2
        else:
            return Conjugation.S2

    def say(self, context):
        ss = list(name)
        if context.is_possessive:
            ss.append(POSSESSIVE_MARK)

        conj = self.decide_conjugation()

        return SayResult(tokens=ss, conjugation=conj, eat_prep=False)
