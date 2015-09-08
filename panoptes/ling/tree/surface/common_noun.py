from collections import defaultdict

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
    (Recursive) noun phrases and bare common nouns, as well as different types
    of proforms that map to this structure.

    Examples:
    * [The dog] barked.
    * [Her dog] is [hers].
    * [That] is good.
    * [Which one] is [that]?
    * [All] are [here].
    * [Everyone] was different [then].
    * [Every idea of Einstein that dogs bark which I don't believe] is true.
    """

    def __init__(self, possessor, correlative, gram_number, gram_of_number,
                 explicit_number, attrs, thing, say_thing, preps_nargs):
        # Possessor.
        #
        # If it has a possessor, correlative must be DEFINITE (eg, "[Tim's] cat"
        # means "[the] cat of Tim").
        #
        # Examples:
        # * [Tim's] cat
        # * [my] cat
        # * [The boy's dog's] doghouse
        self.possessor = possessor
        if self.possessor:
            assert isinstance(self.possessor, Argument)
            assert correlative = SurfaceCorrelative.DEFINITE

        # Grammatical clues about the number (eg, "that cat", "those cats",
        # "every cat", "all cats").  They have to jive with each other.
        #
        # Note that whether the noun is said as plural or singular is derived
        # dynamically, considering exceptions.
        self.correlative = correlative         # SurfaceCorrelative.
        self.gram_number = gram_number         # Roughly how many there are.
        self.gram_of_number = gram_of_number   # Out of roughly how many the
                                               # complete expression matches.
        assert SurfaceCorrealtive.is_valid(self.correlative)
        assert N3.is_valid(self.gram_number)
        assert N5.is_valid(self.gram_of_number)

        # Explicit count or amount that converts to N3.  If present, must match
        # grammatical clues about number above.
        self.explicit_number = explicit_number
        if self.explicit_number:
            assert isinstance(self.explicit_number, Number)

        # List of restrictive or descriptive attributes.
        self.attrs = attrs
        assert isinstance(self.attrs, list)
        for a in self.attrs:
            assert isinstance(a, Attribute)

        # The word(s) for its type, unit, noun, etc.
        #
        # May not be present (eg, "[that kite] flew" vs "[that] flew").
        #
        # Say its type when it is non-obvious from context, otherwise it's more
        # parsimonious not to.
        #
        # If 'say_thing', 'thing' must exist.
        self.thing = thing
        self.say_thing = say_thing
        if self.say_thing or self.thing:
            assert isinstance(self.thing, str)
            assert self.thing

        # Descriptive or restrictive child structures coming after the head.
        # TODO: not used in this demo.
        self.preps_nargs = preps_nargs
        assert isinstance(self.preps_nargs, list)

    def is_interrogative(self):
        if CORRELATIVE2IS_INTERROGATIVE[self.correlative]:
            return True

        if self.possessor:
            if self.possessor.is_interrogative():
                return True

        return False

    def is_relative(self):
        # Ask our possessor (eg, "The castle whose king is fat").
        if self.possessor:
            if self.possessor.is_relative():
                return True

        # Ask our direct children (eg, "The castle the king of which is fat").
        for p, n in self.preps_nargs:
            if n and n.is_relative():
                return True

        return False

    def is_sentient(self):
        """
        -> None, False, or True

        Our personhood matters to the relative pronouns of our child relative
        clauses.

        Eg, "the dog [that] saw you" but "the boy [who] saw you"
        """
        if self.thing:
            return is_thing_sentient(self.thing)
        else:
            return None

    def decide_conjugation(self, state):
        return self.say(state, ARBITRARY_SAY_CONTEXT).conjugation

    def say(self, state, context):
        XXX
