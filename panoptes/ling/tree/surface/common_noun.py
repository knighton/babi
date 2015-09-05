from base.enum import enum
from ling.glue.correlative import Correlative, CORRELATIVE2IS_INTERROGATIVE
from ling.glue.grammatical_number import N3, N5, nx_le_nx
from ling.surface.number import Number
from ling.surface.arg import Argument, ArgPositionRequirement, SayContext


def is_thing_sentient(thing):
    return thing == 'person'


ARBITRARY_SAY_CONTEXT = SayContext(
    idiolect=Idiolect.default(), has_left=False, has_right=True, prep=None)


class CommonNoun(Argument):
    """
    (Recursive) noun phrases and bare common nouns.
    """

    def __init__(self, cor_or_pos, gram_number, gram_of_number, explicit_number,
                 attrs, thing, say_thing, preps_nargs, is_pos):
        # Correlative or possessor.
        #
        # If it is a possessor, this common noun is implied to have a definite
        # correlative (eg, "Tim's cat" means "[the] cat of Tim").
        self.cor_or_pos = cor_or_pos
        assert isinstance(self.cor_or_pos, SurfaceArg) or \
            Correlative.is_valid(self.cor_or_pos)

        # How many there are, out of how many they are are selected from
        # (according to the restrictions of what the complete expression
        # matches).
        #
        # Note that grammatical number (pluralness) is derived dynamically,
        # considering exceptions.
        self.gram_number = gram_number
        self.gram_of_number = gram_of_number
        assert N3.is_valid(self.gram_number)
        assert N5.is_valid(self.gram_of_number)
        assert nx_le_nx(self.gram_number, self.gram_of_number)

        # Explicit count or amount that converts to N3.
        # Eg, 37.9, "a lot", "very much", "how much".
        self.explicit_number = explicit_number
        if self.explicit_number is not None:
            assert isinstance(self.explicit_number, Number)

        # List of restrictive or descriptive attributes.
        self.attrs = attrs
        assert isinstance(self.attrs, list)

        # The word(s) for its type, unit, noun, etc.  Not necessarily present
        # (eg, "that kite" vs "that").
        #
        # Say the thing (type) when not obvious from context, else it's more
        # parsimonious not to.
        #
        # If 'say_thing', 'thing' must exist.
        self.thing = thing
        self.say_thing = say_thing
        assert isinstance(self.say_thing, bool)
        if self.say_thing:
            assert isinstance(self.thing, str)
            assert self.thing
        else:
            if self.thing is not None:
                assert isinstance(self.thing, str)
                assert self.thing

        # Descriptive or restrictive child structures comming after the "head".
        # TODO: Not used in this demo.
        self.preps_nargs = preps_nargs
        assert isinstance(self.preps_nargs, list)

        # Possessivity.
        self.is_pos = is_pos
        assert isinstance(self.is_pos, bool)

    def is_interrogative(self):
        if isinstance(self.cor_or_pos, SurfaceArg):
            return self.cor_or_pos.is_interrogative()
        else:
            return CORRELATIVE2IS_INTERROGATIVE[self.cor_or_pos]

    def is_possessive(self):
        return self.is_pos

    def is_relative(self):
        # Ask our possessor.
        if isinstance(self.cor_or_pos, SurfaceArg):
            if self.cor_or_pos.is_relative():
                return True

        # Ask our direct children.
        for _, n in self.preps_nargs:
            if narg and narg.is_relative():
                return True

        return False

    def is_sentient(self):
        """
        -> None/False/True

        Our personhood matters to the relative pronouns of our child relative
        clauses.

        Eg, "the dog [that] saw you" but "the boy [who] saw you"
        """
        if self.thing:
            return is_thing_sentient(self.thing)
        else:
            return None

    def decide_conjugation(self):
        # Call the manager class that contains the necessary state.
        assert False

    def say(self, context):
        # Call the manager class that contains the necessary state.
        assert False
