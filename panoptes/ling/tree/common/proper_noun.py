from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.glue.magic_token import POSSESSIVE_MARK
from panoptes.ling.glue.relation import RelationArgType
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.surface.base import SayResult


class ProperNoun(CommonArgument):
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

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'ProperNoun',
            'name': list(self.name),
            'is_plur': self.is_plur,
        }

    # --------------------------------------------------------------------------
    # From deep.

    def relation_arg_type(self):
        return RelationArgType.INERT

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        if self.is_plur:
            return Conjugation.P2
        else:
            return Conjugation.S2

    def say(self, state, idiolect, context):
        ss = list(self.name)
        if context.is_possessive:
            ss.append(POSSESSIVE_MARK)
        conj = self.decide_conjugation(state, idiolect, context)
        return SayResult(tokens=ss, conjugation=conj, eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        return ProperNoun(tuple(d['name']), d['is_plur'])
