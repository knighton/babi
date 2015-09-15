from collections import defaultdict

from panoptes.ling.glue.correlative import SurfaceCorrelative
from panoptes.ling.glue.grammatical_number import N3, N5, nx_le_nx_is_possible
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.glue.magic_token import POSSESSIVE_MARK
from panoptes.ling.tree.surface.base import SayContext, SurfaceArgument


def is_noun_sentient(noun):
    return noun == 'person'


class SurfaceCommonNoun(SurfaceArgument):
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
                 explicit_number, attributes, noun, say_noun, preps_nargs):
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
            assert isinstance(self.possessor, SurfaceArgument)
            assert correlative == SurfaceCorrelative.DEFINITE

        # Grammatical clues about the number (eg, "that cat", "those cats",
        # "every cat", "all cats").  They have to jive with each other.
        #
        # Note that whether the noun is said as plural or singular is derived
        # dynamically, considering exceptions.
        self.correlative = correlative         # SurfaceCorrelative.
        self.gram_number = gram_number         # Roughly how many there are.
        self.gram_of_number = gram_of_number   # Out of roughly how many the
                                               # complete expression matches.
        assert SurfaceCorrelative.is_valid(self.correlative)
        assert N3.is_valid(self.gram_number)
        assert N5.is_valid(self.gram_of_number)
        assert nx_le_nx_is_possible(self.gram_number, self.gram_of_number)
        # TODO: crosscheck correlative against grammatical numbers.

        # Explicit count or amount that converts to N3.  If present, must match
        # grammatical clues about number above.
        self.explicit_number = explicit_number
        if self.explicit_number:
            assert False  # NOTE: not in demo.
            # assert isinstance(self.explicit_number, Number)
            # TODO: crosscheck explicit nubmer against grammatical numbers.

        # List of restrictive or descriptive attributes.
        self.attributes = attributes
        assert isinstance(self.attributes, list)
        for a in self.attributes:
            assert False  # NOTE: not in demo.
            # assert isinstance(a, Attribute)

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
            assert isinstance(self.noun, basestring)
            assert self.noun

        # Descriptive or restrictive child structures coming after the head.
        self.preps_nargs = preps_nargs
        assert isinstance(self.preps_nargs, list)
        for p, n in self.preps_nargs:
            assert False  # NOTE: not used in this demo.

        # We can have at most one relative child (eg, "the castle whose king",
        # "the castle the kind of which").
        count = 0
        if self.possessor and self.possessor.is_relative():
            count += 1
        for p, n in self.preps_nargs:
            if n and n.is_relative():
                count += 1
        assert count in (0, 1)

    # --------------------------------------------------------------------------
    # From base.

    def to_d(self):
        if self.possessor:
            pos = self.possessor.to_d()
        else:
            pos = None

        if self.explicit_number:
            num = self.explicit_number.to_d()
        else:
            num = None

        preps_nargs = []
        for prep, arg in self.preps_nargs:
            if arg:
                arg = arg.to_d()
            preps_nargs.append((prep, arg))

        return {
            'type': 'SurfaceCommonNoun',
            'possessor': pos,
            'correlative': SurfaceCorrelative.to_str[self.correlative],
            'gram_number': N3.to_str[self.gram_number],
            'gram_of_number': N5.to_str[self.gram_of_number],
            'explicit_number': num,
            'attributes': map(lambda a: a.to_d(), self.attributes),
            'noun': self.noun,
            'say_noun': self.say_noun,
            'preps_nargs': preps_nargs,
        }

    def is_interrogative(self):
        if self.correlative == SurfaceCorrelative.INTR:
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

    # --------------------------------------------------------------------------
    # From surface.

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

    def decide_conjugation(self, state, idiolect, context):
        return self.say_head(state, idiolect, context).conjugation

    def say_head_as_shortcut(self, state, idiolect, context):
        """
        Eg, therefore
        """
        if self.possessor or self.explicit_number or self.attributes:
            return None

        return state.shortcut_mgr.say(
            context.prep, self.gram_number, self.gram_of_number,
            self.correlative, self.noun, idiolect.archaic_shortcuts)

    def say_head_as_correlative(self, state):
        """
        Eg, what
        """
        if self.possessor or self.explicit_number or self.attributes:
            return None

        return state.correlative_mgr.say(
            self.correlative, self.gram_number, self.gram_of_number, True)

    def say_head_as_possessive_pronoun(self, state, idiolect, context):
        """
        Eg, yours
        """
        if self.explicit_number or self.attributes:
            return None

        if not isinstance(self.possessor, PersonalPronoun):
            return None

        ss = state.personal_mgr.pospro_say(
            self.possessor.declension, idiolect.whom)
        conj = nx_to_nx(self.gram_number, N2)
        eat_prep = False
        return SayResult(ss, conj, eat_prep)

    def say_head_as_number(self, state, idiolect, context):
        """
        Eg, three
        """
        if self.attributes:
            return None

        if self.possessor:
            # Eg, "your three".
            sub_context = SayContext(
                prep=None, has_left=context.has_left, has_right=True,
                is_possessive=True)
            r = self.possessor.say(state, idiolect, sub_context)
            num_has_left = True
        elif self.correlative == SurfaceCorrelative.INDEF:
            # Eg, "three".
            tokens = []
            n2 = nx_to_nx(self.gram_number, N2)
            conj = N2_TO_CONJ[n2]
            eat_prep = False
            r = SayResult(tokens, conj, eat_prep)
            num_has_left = False
        else:
            # Eg, "those three"
            is_pro = False
            r = state.correlative_mgr.say(
                self.correlative, self.gram_number, self.gram_of_number, is_pro)
            num_has_left = True

        # If saying the possessor or the correlative failed (some kind of
        # invalid configuration), bail.
        if not r:
            return None

        # Add the actual number's tokens.
        if num_has_left:
            left = True
        else:
            left = context.has_left

        r2 += self.number.say(None)
        r.tokens += r2.tokens
        return r

    def say_head_as_full(self, state, idiolect, context, override_noun):
        """
        Eg, cats, whichever three wise men
        """
        # Say the front part (correlative or possessive).
        if self.possessor:
            # Say the potentially recursive possessor tree.
            sub_context = SayContext(
                prep=None, has_left=context.has_left, has_right=True,
                is_possessive=True)
            r = self.possessor.say(state, idiolect, sub_context)

            # If that failed, bail.
            if not r:
                return None

            # Get pluralness from grammatical number.
            n2 = nx_to_nx(self.gram_number, N2)
            is_plur = N2 == N2.PLUR
        else:
            # Get the determiner words.
            is_pro = False
            r = state.correlative_mgr.say(
                self.correlative, self.gram_number, self.gram_of_number, is_pro)

            # If saying failed, bail.
            if not r:
                return None

            # If explicit number and indef, don't say the correlative.
            #
            # Eg, "I saw 3 cats"
            if self.explicit_number and \
                    self.correlative == SurfaceCorrelative.INDEF:
                r.tokens = []

            # Get pluralness from its conjugation.
            is_plur = r.conjugation == Conjugation.P3

        # Say the explicit number.
        if self.explicit_number:
            r2 = self.explicit_number.say(state, idiolect, None)
            r.tokens += r2.tokens

        # Say the attributes.
        if self.attributes:
            assert False  # NOTE: not in demo.

        # Say the noun.
        if is_plur:
            s = state.plural_mgr.to_plural(override_noun)
        else:
            s = override_noun
        r.tokens.append(s)

        return r

    def say_head(self, state, idiolect, context):
        # Try various options for rendering it.
        if self.say_noun:
            r = self.say_head_as_shortcut(state, idiolect, context)
            if not r:
                r = self.say_head_as_full(state, idiolect, context, self.noun)
        else:
            r = self.say_head_as_correlative(state)
            if not r:
                r = self.say_head_as_possessive_pronoun(
                    state, idiolect, context)
            if not r:
                self.say_head_as_number(state, idiolect, context)

        # Fall back to tying full as "one" (can still fail if invalid
        # configuration).
        if not r:
            r = self.say_head_as_full(state, idiolect, context, 'one')

        # Crash if the wrong correlative was chosen for its grammatical counts,
        # etc.  Could not happen during parsing.  If this crashes, structure
        # generation code is wrong.
        assert r

        return r

    def say_tail(self, state, idiolect, context):
        if self.preps_nargs:
            assert False  # TOOD: not in MVP.

        return []

    def say(self, state, idiolect, context):
        right = context.has_right or self.preps_nargs
        sub_context = SayContext(
            prep=context.prep, has_left=context.has_left, has_right=right,
            is_possessive=context.is_possessive)
        r = self.say_head(state, sub_context)

        sub_context = SayContext(
            prep=None, has_left=True, has_right=context.has_right,
            is_possessive=False)
        r.tokens += self.say_tail(state, sub_context)

        if context.is_possessive:
            r.tokens.append(POSSESSIVE_MARK)

        return r

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def from_d(d, recursion):
        possessor = recursion.from_d(d['possessor'])
        correlative = SurfaceCorrelative.from_str[d['correlative']]
        gram_number = N3.from_str[d['gram_number']]
        gram_of_number = N5.from_str[d['gram_of_number']]
        explicit_number = recursion.from_d(d['explicit_number'])
        attributes = map(lambda recursion.from_d, d['attributes'])
        noun = d['noun']
        say_noun = d['say_noun']

        preps_nargs = []
        for prep, arg in d['preps_nargs']:
            if arg:
                arg = recursion.from_d(arg)
            preps_nargs.append((prep, arg))

        return SurfaceCommonNoun(
            possessor, correlative, gram_number, gram_of_number,
            explicit_number, attributes, noun, say_noun)
