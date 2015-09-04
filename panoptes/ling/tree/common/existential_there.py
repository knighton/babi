from ling.common.base import Argument, ArgPositionRestriction, SayResult


class ExistentialThere(Argument):
    """
    Existential there as a verb argument.

    Eg, "[There] are cats here.", "Because of the cats, [there] are fewer mice".
    """

    def arg_position_restriction(self):
        return ArgPositionRestriction.SUBJECT

    def decide_conjugation(self):
        return None

    def say(self, context):
        return SayResult(tokens=['there'], conjugation=None, eat_prep=False)
