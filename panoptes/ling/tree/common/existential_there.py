from panoptes.ling.tree.common.base import *


class ExistentialThere(Argument):
    """
    Existential there as a verb argument.

    Eg, "[There] are cats here.", "Because of the cats, [there] are fewer mice".
    """

    def arg_position_restriction(self):
        return ArgPositionRestriction.SUBJECT

    def decide_conjugation(self, state):
        # Returning None instead of a Conjugation means that it will take the
        # conjugation of the verb's object instead.
        return None

    def say(self, state, context):
        return SayResult(tokens=['there'], conjugation=None, eat_prep=False)
