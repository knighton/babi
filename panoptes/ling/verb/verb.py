from base import enum
from ling.glue.inflection import Conjugation


class Polarity(object):
    """
    Linguistic polarity (English).
    """

    def __init__(self, tf, is_contrary):
        # The actual truth value.
        #
        # "You said" vs "You didn't say".
        self.tf = tf
        assert isinstance(self.tf, bool)

        # Whether the truth value is contrary to expectations.
        #
        # "You said X" vs "You *did* say X".
        self.is_contrary = is_contrary
        assert self.is_contrary in (None, False, True)


class Aspect(object):
    """
    Linguistic aspect (English).
    
    Just enough to handle the different renderings, nothing more.
    """

    def __init__(self, is_perf, is_prog):
        self.is_perf = is_perf
        assert isinstance(self.is_perf, bool)

        self.is_prog = is_prog
        assert isinstance(self.is_prog, bool)


# Modal "flavor".
#
# * Moods and modal verbs distinguish these (in English).
#
# * There are other modality-like meanings performed by regular verbs and
#   adverbs, but those are outside our scope here (we are just representing
#   things).
#
# * Instead of 'conditional' being a modality, modalities have normal and
#   conditional forms (so conditional + indicative is bare 'conditional').  This
#   is because of relations like 'can + would = could'.
#
# * The two subjunctives:
#       SBJ_CF ('subjunctive-counterfactual') "if he [were] smart"
#       SBJ_IMP ('subjunctive-imperative') "he requests you [come]"
ModalFlavor = enum.new("""ModalFlavor =
    INDICATIVE
    SBJ_CF

    DEDUCTIVE
    ALMOST_CERTAIN
    PROBABLE
    POSSIBLE

    IMPERATIVE
    SBJ_IMP
    ABILITY
    PERMISSION
    NORMATIVE
    NECESSITY
""")


class Modality(object):
    def __init__(self, flavor, is_cond):
        self.flavor = flavor
        assert ModalFlavor.is_valid(self.flavor)

        self.is_cond = is_cond
        assert isinstance(self.is_cond, bool)

    def is_indicative(self):
        return self.flavor == ModalFlavor.INDICATIVE and not self.is_cond


# Abstract sense of tense that is actually about time only.
Tense = enum.new('Tense = PAST PRESENT FUTURE')


# Deep verb form splits gerund for usage higher up in the codebase.
VerbForm = enum.new('VerbForm = FINITE BARE_INF TO_INF GERUND SUBJLESS_GERUND')


class DeepVerb(object):
    """
    The collection of concepts underlying a verb that are intrinsic to it, like
    polarity, aspect, etc.

    Used in deep structure.

    Note that there are combinations of values that are invalid.
    """

    def __init__(self, lemma, polarity, tense, aspect, modality, verb_form,
                 is_pro_verb):
        # Lemma is blank if it's a pro-verb.
        self.lemma = lemma
        if self.lemma is not None:
            assert self.lemma
            assert isinstance(self.lemma, str)
            assert self.lemma.islower()

        self.polarity = polarity
        assert isinstance(self.polarity, Polarity)

        self.tense = tense
        assert self.tense is None or Tense.is_valid(self.tense)

        self.aspect = aspect
        assert isinstance(self.aspect, Aspect)

        self.modality = modality
        assert isinstance(self.modality, Modality)

        self.verb_form = verb_form
        assert VerbForm.is_valid(self.verb_form)

        self.is_pro_verb = is_pro_verb
        assert isinstance(self.is_pro_verb, bool)


# Linguistic voice.
Voice = enum.new('Voice = ACTIVE PASSIVE')


# Relative containment.
#
# Whether the verb is in a relative clause, and if so, what kind of relative
# pronoun.
#
# ZERO     "the man [seen] by you"
# WORD     "the man that [was seen] by you"
# NOT_REL  "the man [was seen] by you"
#
# ZERO
# - Meaning: it is the verb of a relative clause; relative pronoun is a zero.
# - verb_form restriction: must be finite.
# - Surface verb_form handling: use SurfaceVerbForm.ZERO_RELCLAUSE_FINITE
#   instead of SurfaceVerbForm.NORMAL_FINITE (eg, "the cat [seen] by you" vs
#   "the cat that [was seen] by you").
#
# WORD
# - Meaning: is the verb of a relative clause; relative pronoun is not a zero.
# - verb_form restriction: must be finite.
# - Surface verb_form handling: use SurfaceVerbForm.NORMAL_FINITE.
#
# NOT_REL
# - Meaning: is not part of a relative clause.
# - verb_form restriction: any of them is ok.
# - Surface verb_form handling; normal (NORMAL_FINITE for finite).
RelativeContainment = enum.new('RelativeContainment = ZERO WORD NOT_REL')


# Subjunctive handling.
#
# WERE_SBJ  "If I [were] an astronaut"
# WAS_SBJ   "If I [was] an astronaut"
SubjunctiveHandling = enum.new('SubjunctiveHandling = WERE_SBJ WAS_SBJ')


class SurfaceVerb(object):
    """
    A DeepVerb paired with concepts underlying verbs that tell us about their
    surroundings instead of the verb itself, like voice, conjugation, and so on.

    Used in surface structure.
    """

    def __init__(self, intrinsics, voice, conj, is_split, relative_cont,
                 contract_not, split_inf, sbj_handling):
        self.intrinsics = intrinsics
        assert isinstance(self.intrinsics, DeepVerb)

        self.voice = voice
        assert Voice.is_valid(self.voice)

        self.conj = conj
        assert conj is None or Conjugation.is_valid(self.conj)

        self.is_split = is_split
        assert isinstance(self.is_split, bool)

        self.relative_cont = relative_cont
        assert RelativeContainment.is_valid(self.relative_cont)

        self.contract_not = contract_not
        assert self.contract_not in (None, False, True)

        self.split_inf = split_inf
        assert self.split_inf in (None, False, True)

        self.sbj_handling = sbj_handling
        assert self.sbj_handling is None or \
            SubjunctiveHandling.is_valid(self.sbj_handling)
