from panoptes.etc.enum import enum


ArgPosRestriction = enum('ArgPosRestriction = SUBJECT NOT_SUBJECT ANYWHERE')


class BaseArgument(object):
    """
    A standalone (a) verb argument or (b) child of a noun phrase.

    These objects are used in surface structure and deep structure.  We use two
    different levels of structure in order to apply and reverse transformations
    like fronting, keeping everything else pretty much the same.

    These are not directly instantiated.  Instead, instantiate a SurfaceArgument
    or DeepArgument, which inherit from this.  CommonArgument, which is pretty
    much everything that does not have complicated structure, inherits from both
    of those.

    Technically, sometimes an argument can be used as a non-standalone component
    of another argument, such as Attributes and Numbers inside a CommonNoun, but
    it will always be able to be used on its own.
    """

    def dump(self):
        """
        -> dict

        Return a dict that can be used to reconstruct ourselves, containing
        nothing but primitive types and the string names of enum values.
        """
        raise NotImplementedError

    def is_interrogative(self):
        """
        -> bool

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
        return False

    def is_relative(self):
        """
        -> bool

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
        return False

    def arg_position_restriction(self):
        """
        -> ArgPosRestriction

        Get whether we must be the subject (existential "there"), cannot be the
        subject ("me"), could be ("you"), etc.
        """
        return ArgPosRestriction.ANYWHERE
