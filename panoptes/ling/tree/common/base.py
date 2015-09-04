from base.enum import enum
from ling.glue.inflection import Conjugation


ArgPosRestriction = enum('ArgPosRestriction = SUBJECT OBJECT ANYWHERE')


class SayContext(object):
    """
    Input to saying.
    """

    def __init__(self, idiolect, has_left, has_right, prep, is_possessive):
        # Various knobs on how things are said.
        self.idiolect = idiolect

        # When an object is to be delimited by commas on either side, you don't
        # if there's nothing there on that side.
        self.has_left = has_left
        self.has_right = has_right

        # The preposition matters because sometimes the argument absors the prep
        # when it is said (eg, (because of, what reason) -> "why").
        self.prep = prep

        # Whether it needs to be said in its possessive form.
        self.is_possessive = is_possessive

    def check(self):
        assert isinstance(self.idiolect, Idiolect)
        assert isinstance(self.has_left, bool)
        assert isinstance(self.has_right, bool)
        if self.prep:
            assert isinstance(self.prep, tuple)
        assert isinstance(self.is_possessive, bool)


class SayResult(object):
    """
    Output from saying.
    """

    def __init__(self, tokens, conjugation, eat_prep):
        self.tokens = tokens
        self.conjugation = conjugation
        self.eat_prep = eat_prep

    def check(self):
        assert isinstance(self.tokens, list)
        for s in self.tokens:
            assert isinstance(s, str)

        if self.conjugation is not None:
            assert Conjugation.is_valid(self.conjugation)

        assert isinstance(self.eat_prep, bool)


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
        return False

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
        return False

    def arg_position_restriction(self):
        """
        -> ArgPosRestriction

        Get whether we must be the subject (existential "there"), cannot be the
        subject ("me"), could be ("you"), etc.
        """
        return ArgPosRestriction.ANYWHERE

    def decide_conjugation(self):
        """
        -> Conjugation or None

        Decide the conjugation of the verb if we are the subject.  Dies if we
        cannot be the subject (arg_position_restriction()).  For existential
        there, this will return None, and the caller must use the verb object's
        conjugation instead.

        This is cheaper than saying the whole thing for large noun phrases and
        the like.
        """
        raise NotImplementedError

    def say(self, context):
        """
        SayContext -> SayResult

        Render this object (to words, a conjugation, whether to drop the
        referring preposition, etc).

        Some more complicated objects depend on external state to be said, so
        this call may raise an exception.
        """
        raise NotImplementedError
