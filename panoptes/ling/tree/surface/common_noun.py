from collections import defaultdict

from ling.glue.correlative import Correlative, CORRELATIVE2IS_INTERROGATIVE
from ling.glue.grammatical_number import N3, N5, nx_le_nx
from ling.surface.number import Number
from ling.surface.arg import Argument, ArgPositionRequirement, SayContext


def is_noun_sentient(noun):
    return noun == 'person'


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
                 explicit_number, attrs, noun, say_noun, preps_nargs):
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
        # Say the noun when it is non-obvious from context, otherwise it's more
        # parsimonious not to.
        #
        # If 'say_noun', 'noun' must exist.
        self.noun = noun
        self.say_noun = say_noun
        if self.say_noun or self.noun:
            assert isinstance(self.noun, str)
            assert self.noun

        # Descriptive or restrictive child structures coming after the head.
        # TODO: not used in this demo.
        self.preps_nargs = preps_nargs
        assert isinstance(self.preps_nargs, list)

        # At most one argument can be fronted (therefore missing from its
        # original position).
        count = 0
        for p, n in self.preps_nargs:
            if not n:
                count += 1
        assert count in (0, 1)

        # We can have at most one relative child (eg, "the castle whose king",
        # "the castle the kind of which").
        count = 0
        if self.possessor and self.possessor.is_relative():
            count += 1
        for p, n in self.preps_nargs:
            if n and n.is_relative():
                count += 1
        assert count in (0, 1)

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
        if self.noun:
            return is_noun_sentient(self.noun)
        else:
            return None

    def decide_conjugation(self, state):
        return self.say(state, ARBITRARY_SAY_CONTEXT).conjugation

    def say_head_as_shortcut(self, state, context):
        if self.possessor or self.explicit_number or self.attrs:
            return None

        return state.shortcut_mgr.say(
            context.prep, self.gram_number, self.gram_of_number,
            self.correlative, self.noun,
            context.idiolect.allow_archaic_shortcuts)

    def say_head_as_correlative(self, state, context):
        if self.possessor or self.explicit_number or self.attrs:
            return None

        return state.correlative_mgr.say(
            self.correlative, self.gram_number, self.gram_of_number, True)

    def say_head_as_number(self, state, context):
        XXX

    def say_head_as_full(self, state, context, override_noun):
        XXX

    def say_head(self, state, context):
        # Try various options for rendering it.
        if self.say_noun:
            r = self.say_head_as_shortcut(state, context)
            if not r:
                r = self.say_head_as_full(state, context, self.noun)
        else:
            r = self.say_head_as_correlative(state, context)
            if not r:
                self.say_head_as_number(state, context)

        # Fall back to tying full as "one" (can still fail if invalid
        # configuration).
        if not r:
            r = self.say_head_as_full(state, context, 'one')

        # Crash if the wrong correlative was chosen for its grammatical counts,
        # etc.  Could not happen during parsing.  If this crashes, structure
        # generation code is wrong.
        assert r

        return r

    def say(self, state, context):
        left = context.has_left
        right = context.has_right or self.preps_nargs
        sub_context = SayContext(
            context.idiolect, left, right, context.prep, context.is_possessive)
        r = self.say_head(state, context)

        XXX
