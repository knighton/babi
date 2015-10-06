from collections import defaultdict

from panoptes.ling.glue.grammatical_number import N2, N3, N5, \
    nx_le_nx_is_possible, nx_to_nx
from panoptes.ling.glue.inflection import Conjugation, N2_TO_CONJ
from panoptes.ling.glue.magic_token import POSSESSIVE_MARK
from panoptes.ling.tree.common.number import Number
from panoptes.ling.tree.common.util.selector import Selector
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

    def __init__(self, possessor=None, selector=None, number=None,
                 attributes=None, noun=None, preps_nargs=None):
        # Prevent aliasing hell.
        if attributes is None:
            attributes = []
        if preps_nargs is None:
            preps_nargs = []

        # Possessor.
        #
        # If it has a possessor, selector/correlative must be definite (eg,
        # "[Tim's] cat" means "[the] cat of Tim").
        #
        # Examples:
        # * [Tim's] cat
        # * [my] cat
        # * [The boy's dog's] doghouse
        self.possessor = possessor
        if self.possessor:
            assert isinstance(self.possessor, SurfaceArgument)
            assert selector.is_definite()

        # Grammatical clues about the number (eg, "that cat", "those cats",
        # "every cat", "all cats").  They have to jive with each other.
        #
        # Note that whether the noun is said as plural or singular is derived
        # dynamically, considering exceptions.
        self.selector = selector
        assert isinstance(self.selector, Selector)

        # Explicit count or amount that converts to N3.  If present, must match
        # grammatical clues about number above.
        self.number = number
        if self.number:
            assert isinstance(self.number, Number)
            #assert self.selector.accepts_count_or_amount(self.number)  TODO

        # List of restrictive or descriptive attributes.
        self.attributes = attributes
        assert isinstance(self.attributes, list)
        for s in self.attributes:
            assert s
            assert isinstance(s, basestring)

        # The word(s) for its type, unit, noun, etc.
        #
        # May not be present (eg, "[that kite] flew" vs "[that] flew").  May be
        # present as a pro-adverb/pronoun (eg, "everyone", "everywhere").
        #
        # Say the noun when it is non-obvious from context, otherwise it's more
        # parsimonious not to.
        self.noun = noun
        if self.noun:
            assert isinstance(self.noun, basestring)

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

    def is_sentient(self):
        """
        -> bool

        Our personhood matters to the relative pronouns of our child relative
        clauses.

        Noun is always present when the object has children.

        Eg, "the dog [that] saw you" but "the boy [who] saw you"
        """
        assert self.noun
        return is_noun_sentient(self.noun)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        if self.possessor:
            pos = self.possessor.dump()
        else:
            pos = None

        if self.number:
            num = self.number.dump()
        else:
            num = None

        preps_nargs = []
        for prep, arg in self.preps_nargs:
            if arg:
                arg = arg.dump()
            preps_nargs.append([prep, arg])

        return {
            'type': 'SurfaceCommonNoun',
            'possessor': pos,
            'selector': self.selector.dump(),
            'number': num,
            'attributes': self.attributes,
            'noun': self.noun,
            'preps_nargs': preps_nargs,
        }

    def is_interrogative(self):
        if self.selector.is_interrogative():
            return True

        if self.number and self.number.is_interrogative():
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

    def has_hole(self):
        for p, n in self.preps_nargs:
            if not n:
                return True
        return False

    def put_fronted_arg_back(self, what):
        for i, (p, n) in enumerate(self.preps_nargs):
            if not n:
                self.preps_nargs[i][1] = what
                return

        assert False

    def decide_conjugation(self, state, idiolect, context):
        return self.say_head(state, idiolect, context).conjugation

    def say_head_as_pro_adverb(self, state, idiolect, context):
        """
        Eg, therefore
        """
        if self.possessor or self.number or self.attributes:
            return None

        return state.pro_adverb_mgr.say(context.prep, self.selector, self.noun,
                                        idiolect.archaic_pro_adverbs)

    def say_head_as_impersonal_pronoun(self, state):
        """
        Eg, what
        """
        if self.possessor or self.number or self.attributes:
            return None

        return state.det_pronoun_mgr.say_pronoun(self.selector)

    def say_head_as_possessive_pronoun(self, state, idiolect, context):
        """
        Eg, yours
        """
        if self.number or self.attributes:
            return None

        if not isinstance(self.possessor, PersonalPronoun):
            return None

        ss = state.personal_mgr.pospro_say(
            self.possessor.declension, idiolect.whom)
        n2 = self.selector.guess_n(N2)
        conj = N2_TO_CONJ[n2]
        return SayResult(tokens=ss, conjugation=conj, eat_prep=False)

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
        elif self.selector.is_indefinite():
            # Eg, "three".
            n2 = self.selector.guess_n(N2)
            conj = N2_TO_CONJ[n2]
            r = SayResult(tokens=[], conjugation=conj, eat_prep=False)
            num_has_left = False
        else:
            # Eg, "those three"
            r = state.det_pronoun_mgr.say_determiner(self.selector)
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
            n2 = self.selector.guess_n(N2)
            is_plur = n2 == N2.PLUR

            # Its possessor doesn't affect its conjugation, just its number.
            r.conjugation = N2_TO_CONJ[n2]
        else:
            # Get the determiner words.
            r = state.det_pronoun_mgr.say_determiner(self.selector)

            # If saying failed, bail.
            if not r:
                return None

            # If explicit number and indef, don't say the correlative.
            #
            # Eg, "I saw 3 cats"
            if self.number and self.selector.is_indefinite():
                r.tokens = []

            # Get pluralness from its conjugation.
            is_plur = r.conjugation == Conjugation.P3

        # Say the explicit number.
        if self.number:
            r2 = self.number.say(state, idiolect, None)
            r.tokens += r2.tokens

        # Say the attributes.
        r.tokens += self.attributes

        # Say the noun.
        if is_plur:
            s = state.plural_mgr.to_plural(override_noun)
        else:
            s = override_noun
        r.tokens.append(s)

        return r

    def say_head(self, state, idiolect, context):
        # Try various options for rendering it.
        if self.noun:
            r = self.say_head_as_pro_adverb(state, idiolect, context)
            if not r:
                r = self.say_head_as_full(state, idiolect, context, self.noun)
        else:
            r = self.say_head_as_impersonal_pronoun(state)
            if not r:
                r = self.say_head_as_possessive_pronoun(state, idiolect,
                                                        context)
            if not r:
                self.say_head_as_number(state, idiolect, context)

        # Fall back to tying full as "one" (can still fail if invalid
        # configuration).
        if not r:
            r = self.say_head_as_full(state, idiolect, context, 'one')

        # Crash if the wrong correlative was chosen for its grammatical counts,
        # etc.  Could not happen during parsing.  If this crashes, structure
        # generation code is wrong.
        try:
            assert r
        except:
            print self.dump()
            raise

        return r

    def say_tail(self, state, idiolect, context):
        if self.preps_nargs:
            assert False  # NOTE: not in demo.

        return []

    def say(self, state, idiolect, context):
        right = context.has_right or self.preps_nargs
        sub_context = SayContext(
            prep=context.prep, has_left=context.has_left, has_right=right,
            is_possessive=context.is_possessive)
        r = self.say_head(state, idiolect, sub_context)

        sub_context = SayContext(
            prep=None, has_left=True, has_right=context.has_right,
            is_possessive=False)
        r.tokens += self.say_tail(state, idiolect, sub_context)

        if context.is_possessive:
            r.tokens.append(POSSESSIVE_MARK)

        return r

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        possessor = loader.load(d['possessor'])
        selector = Selector.load(d['selector'])
        number = loader.load(d['number'])
        attributes = map(loader.load, d['attributes'])
        noun = d['noun']

        preps_nargs = []
        for prep, arg in d['preps_nargs']:
            if arg:
                arg = loader.load(arg)
            preps_nargs.append((prep, arg))

        return SurfaceCommonNoun(possessor, selector, number, attributes, noun,
                                 preps_nargs)
