from panoptes.ling.tree.base import ArgPosRestriction
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.surface.base import SayResult


class ExistentialThere(CommonArgument):
    """
    Existential there as a verb argument.

    Eg, "[There] are cats here.", "Because of the cats, [there] are fewer mice".
    """

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'ExistentialThere',
        }

    def arg_position_restriction(self):
        return ArgPosRestriction.SUBJECT

    # --------------------------------------------------------------------------
    # From deep.

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        # Returning None instead of a Conjugation means that it will take the
        # conjugation of the verb's object instead.
        return None

    def say(self, state, idiolect, context):
        return SayResult(tokens=['there'], conjugation=None, eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        return ExistentialThere()
