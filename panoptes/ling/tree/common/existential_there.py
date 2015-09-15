from panoptes.ling.glue.relation import RelationArgType
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.surface.base import SayResult


class ExistentialThere(CommonArgument):
    """
    Existential there as a verb argument.

    Eg, "[There] are cats here.", "Because of the cats, [there] are fewer mice".
    """

    # --------------------------------------------------------------------------
    # From base.

    def to_d(self):
        return {
            'type': 'ExistentialThere',
        }

    def arg_position_restriction(self):
        return ArgPositionRestriction.SUBJECT

    # --------------------------------------------------------------------------
    # From deep.

    def relation_arg_type(self):
        return RelationArgType.INERT

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state):
        # Returning None instead of a Conjugation means that it will take the
        # conjugation of the verb's object instead.
        return None

    def say(self, state, context):
        return SayResult(tokens=['there'], conjugation=None, eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def from_d(d, recursion):
        return ExistentialThere()
