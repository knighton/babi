from base.enum import enum


ArgPosRestriction = enum('ArgPosRestriction = SUBJECT OBJECT ANY')


class Argument(object):
    """
    A standalone argument of a verb of child of a noun phrase.

    SurfaceArgument and DeepArgument inherit from this.
    """

    def is_interrogative(self):
        """
        Whether we raise a question.  If we do, we should be fronted during
        surface-to-deep structure transformation if we are the only
        'interrogative' or focused-on argument.

        Examples:
        * "who" (pronoun)
        * "how few"
        * "how far"
        * "how red"

        TODO: handle -ever correlative correctly.
        """
        raise NotImplementedError

    def is_relative(self):
        """
        Whether this arg either is a relative pronoun, or contains one in a
        direct child prepositional phrase or possessive.

        Examples:
        * "that" (relative pronoun)
        * "who" (relative pronoun)
        * "whose"
        * "whose plan"
        * "the cat of which"
        * but not "the idea that you thought of" because the relative stuff is
          completely contained inside the phrase.
        """
        raise NotImplementedError

    def arg_position_requirement(self):
        """
        -> ArgPosRestriction

        Get whether we must be the subject (existential "there"), cannot be the
        subject ("me"), could be ("you"), etc.
        """
        raise NotImplementedError
