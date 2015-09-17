from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Conjugation


class Polarity(object):
    """
    Linguistic polarity (English).
    """

    def __init__(self, tf, is_contrary):
        # The actual truth value.
        #
        # "You said" vs "You didn't say".
        self.tf = tf

        # Whether the truth value is contrary to expectations.
        #
        # "You said X" vs "You *did* say X".
        self.is_contrary = is_contrary

        self.check()

    def check(self, allow_wildcards=True):
        assert isinstance(self.tf, bool)
        if allow_wildcards:
            assert self.is_contrary in (None, False, True)
        else:
            assert isinstance(self.is_contrary, bool)

    def dump(self):
        return {
            'tf': self.tf,
            'is_contrary': self.is_contrary,
        }

    @staticmethod
    def load(d):
        return Polarity(d['tf'], d['is_contrary'])


class Aspect(object):
    """
    Linguistic aspect (English).
    
    Just enough to handle the different renderings, nothing more.
    """

    def __init__(self, is_perf, is_prog):
        self.is_perf = is_perf

        # TODO: check where is_prog is wildcarded.
        self.is_prog = is_prog
        self.check()

    def check(self, allow_wildcards=True):
        if allow_wildcards:
            assert self.is_perf in (None, False, True)
            assert self.is_prog in (None, False, True)
        else:
            assert isinstance(self.is_perf, bool)
            assert isinstance(self.is_prog, bool)

    def dump(self):
        return {
            'is_perf': self.is_perf,
            'is_prog': self.is_prog,
        }

    @staticmethod
    def load(d):
        return Aspect(d['is_perf'], d['is_prog'])


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
#       SUBJUNCTIVE_CF ('subjunctive-counterfactual') "if he [were] smart"
#       SUBJUNCTIVE_IMP ('subjunctive-imperative') "he requests you [come]"
ModalFlavor = enum("""ModalFlavor =
    INDICATIVE
    SUBJUNCTIVE_CF

    DEDUCTIVE
    ALMOST_CERTAIN
    PROBABLE
    POSSIBLE

    IMPERATIVE
    SUBJUNCTIVE_IMP
    ABILITY
    PERMISSIVE
    NORMATIVE
    NECESSITY
""")


class Modality(object):
    def __init__(self, flavor, is_cond):
        self.flavor = flavor
        self.is_cond = is_cond  # TODO: check where is_cond is wildcarded.
        self.check()

    def check(self, allow_wildcards=True):
        assert ModalFlavor.is_valid(self.flavor)
        if allow_wildcards:
            assert self.is_cond in (None, False, True)
        else:
            assert isinstance(self.is_cond, bool)

    def dump(self):
        return {
            'flavor': ModalFlavor.to_str[self.flavor],
            'is_cond': self.is_cond,
        }

    def is_imperative(self):
        return self.flavor == ModalFlavor.IMPERATIVE

    def is_indicative(self):
        return self.flavor == ModalFlavor.INDICATIVE and not self.is_cond

    def is_subjunctive(self):
        return self.flavor in \
            (ModalFlavor.SUBJUNCTIVE_CF, ModalFlavor.SUBJUNCTIVE_IMP)

    @staticmethod
    def load(d):
        flavor = ModalFlavor.from_str[d['flavor']]
        return Modality(flavor, d['is_cond'])


# Abstract sense of tense that is actually about time only.
Tense = enum('Tense = PAST PRESENT FUTURE')


# Deep verb form splits gerund for usage higher up in the codebase.
VerbForm = enum('VerbForm = FINITE BARE_INF TO_INF GERUND SUBJLESS_GERUND')


class DeepVerb(object):
    """
    The collection of concepts underlying a verb that are intrinsic to it, like
    polarity, aspect, etc.

    Used in deep structure.

    Note that there are combinations of fields that are invalid.
    """

    def __init__(self, lemma, polarity, tense, aspect, modality, verb_form,
                 is_pro_verb):
        self.lemma = lemma
        self.polarity = polarity
        self.tense = tense
        self.aspect = aspect
        self.modality = modality
        self.verb_form = verb_form
        self.is_pro_verb = is_pro_verb

    def check(self, allow_wildcards=True):
        # Lemma is blank if it's a pro-verb.
        if self.lemma is not None:
            assert self.lemma
            assert isinstance(self.lemma, str)
            assert self.lemma.islower()
        assert isinstance(self.polarity, Polarity)
        self.polarity.check(allow_wildcards)
        assert self.tense is None or Tense.is_valid(self.tense)
        assert isinstance(self.aspect, Aspect)
        self.aspect.check(allow_wildcards)
        assert isinstance(self.modality, Modality)
        self.modality.check(allow_wildcards)
        assert VerbForm.is_valid(self.verb_form)
        assert isinstance(self.is_pro_verb, bool)

    def is_finite(self):
        return self.verb_form == VerbForm.FINITE

    def is_imperative(self):
        return self.modality.is_imperative()

    def is_subjunctive(self):
        return self.modality.is_subjunctive()

    def dump(self):
        if self.tense:
            tense = Tense.to_str[self.tense]
        else:
            tense = self.tense
        return {
            'lemma': self.lemma,
            'polarity': self.polarity.dump(),
            'tense': tense,
            'aspect': self.aspect.dump(),
            'modality': self.modality.dump(),
            'verb_form': VerbForm.to_str[self.verb_form],
            'is_pro_verb': self.is_pro_verb,
        }

    @staticmethod
    def load(d):
        polarity = Polarity.load(d['polarity'])
        tense = Tense.from_str[d['tense']]
        aspect = Aspect.load(d['aspect'])
        modality = Modality.load(d['modality'])
        verb_form = VerbForm.from_str[d['verb_form']]
        return DeepVerb(d['lemma'], polarity, tense, aspect, modality,
                        verb_form, d['is_pro_verb'])


# Linguistic voice.
Voice = enum('Voice = ACTIVE PASSIVE')


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
RelativeContainment = enum('RelativeContainment = ZERO WORD NOT_REL')


# Subjunctive handling.
#
# WERE_SBJ  "If I [were] an astronaut"
# WAS_SBJ   "If I [was] an astronaut"
SubjunctiveHandling = enum('SubjunctiveHandling = WERE_SBJ WAS_SBJ')


class SurfaceVerb(object):
    """
    A DeepVerb paired with concepts underlying verbs that tell us about their
    surroundings instead of the verb itself, like voice, conjugation, and so on.

    Used in surface structure.

    Note that there are combinations of fields that are invalid.
    """

    def __init__(self, intrinsics, voice, conj, is_split, relative_cont,
                 contract_not, split_inf, sbj_handling):
        self.intrinsics = intrinsics
        self.voice = voice
        self.conj = conj
        self.is_split = is_split
        self.relative_cont = relative_cont
        self.contract_not = contract_not
        self.split_inf = split_inf
        self.sbj_handling = sbj_handling

    def check(self, allow_wildcards=True):
        assert isinstance(self.intrinsics, DeepVerb)
        self.intrinsics.check(allow_wildcards)
        assert Voice.is_valid(self.voice)
        assert isinstance(self.is_split, bool)
        assert RelativeContainment.is_valid(self.relative_cont)
        if allow_wildcards:
            assert conj is None or Conjugation.is_valid(self.conj)
            assert self.contract_not in (None, False, True)
            assert self.split_inf in (None, False, True)
            assert self.sbj_handling is None or \
                SubjunctiveHandling.is_valid(self.sbj_handling)
        else:
            assert Conjugation.is_valid(self.conj)
            assert isinstance(self.contract_not, bool)
            assert isinstance(self.split_inf, bool)
            assert SubjunctiveHandling.is_valid(self.sbj_handling)

    def to_tuple(self):
        i = self.intrinsics
        return (i.lemma, i.polarity.tf, i.polarity.is_contrary, i.tense,
                i.aspect.is_prog, i.aspect.is_perf, i.modality.flavor,
                i.modality.is_cond, i.verb_form, i.is_pro_verb, self.voice,
                self.conj, self.is_split, self.relative_cont, self.contract_not,
                self.split_inf, self.sbj_handling)

    def to_int_tuple(self, options_per_field):
        """
        Does not allow fields to be None.
        """
        aa = self.to_tuple()
        nn = []
        for a, options in zip(aa, options_per_field):
            nn.append(options.index(a))
        return nn

    def can_be_in_root_clause(self):
        # Most non-indicative moods are banned.
        #
        # "I wish I were here", "she requests you come", etc.
        if self.intrinsics.modality.flavor in \
                (ModalFlavor.SUBJUNCTIVE_CF, ModalFlavor.SUBJUNCTIVE_IMP):
            return False

        # The verb has to be finite (conjugated).
        if self.intrinsics.verb_form != VerbForm.FINITE:
            return False

        # We can't be inside a relative clause at root.
        if self.relative_cont != RelativeContainment.NOT_REL:
            return False

        return True

    def is_finite(self):
        return self.intrinsics.is_finite()

    def is_imperative(self):
        return self.intrinsics.is_imperative()

    def is_subjunctive(self):
        return self.intrinsics.is_subjunctive()

    def dump(self):
        if self.conj:
            conj = Conjugation.to_str[self.conj]
        else:
            conj = self.conj
        if self.sbj_handling:
            sbj = SubjunctiveHandling.to_str[self.sbj_handling]
        else:
            sbj = self.sbj_handling
        return {
            'intrinsics': self.intrinsics.dump(),
            'voice': Voice.to_str[self.voice],
            'conj': conj,
            'is_split': self.is_split,
            'relative_cont': RelativeContainment.to_str[self.relative_cont],
            'contract_not': self.contract_not,
            'split_inf': self.split_inf,
            'sbj_handling': sbj,
        }

    @staticmethod
    def all_options(lemmas, is_pro_verb_options):
        bools = [False, True]

        lemma = lemmas

        tf = bools
        is_contrary = bools

        tense = sorted(Tense.values)

        is_prog = bools
        is_perf = bools

        flavor = sorted(ModalFlavor.values)
        is_cond = bools

        verb_form = sorted(VerbForm.values)

        is_pro_verb = is_pro_verb_options

        voice = sorted(Voice.values)
        conj = sorted(Conjugation.values)
        is_split = bools
        relative_cont = sorted(RelativeContainment.values)
        contract_not = bools
        split_inf = bools
        sbj_handling = sorted(SubjunctiveHandling.values)

        return lemma, tf, is_contrary, tense, is_prog, is_perf, flavor, \
               is_cond, verb_form, is_pro_verb, voice, conj, is_split, \
               relative_cont, contract_not, split_inf, sbj_handling

    @staticmethod
    def finite_options(lemmas, is_pro_verb_options):
        aaa = list(SurfaceVerb.all_options(lemmas, is_pro_verb_options))
        aaa[8] = [VerbForm.FINITE]
        return aaa

    @staticmethod
    def nonfinite_options(lemmas, is_pro_verb_options):
        aaa = list(SurfaceVerb.all_options(lemmas, is_pro_verb_options))
        aaa[6] = [ModalFlavor.INDICATIVE]
        del aaa[8][0] 
        aaa[12] = [False]
        return aaa

    @staticmethod
    def from_tuple(aa):
        lemma, tf, is_contrary, tense, is_prog, is_perf, flavor, \
            is_cond, verb_form, is_pro_verb, voice, conj, is_split, \
            relative_cont, contract_not, split_inf, sbj_handling = aa
        polarity = Polarity(tf, is_contrary)
        aspect = Aspect(is_prog, is_perf)
        modality = Modality(flavor, is_cond)
        intrinsics = DeepVerb(
            lemma, polarity, tense, aspect, modality, verb_form, is_pro_verb)
        return SurfaceVerb(intrinsics, voice, conj, is_split, relative_cont,
                           contract_not, split_inf, sbj_handling)

    @staticmethod
    def from_int_tuple(nn, options_per_field):
        """
        Allows Nones, in which n == number options.
        """
        aa = []
        for n, options in zip(nn, options_per_field):
            if n == len(options):
                a = None
            else:
                a = options[n]
            aa.append(a)
        return SurfaceVerb.from_tuple(aa)

    @staticmethod
    def load(d):
        intrinsics = DeepVerb.load(d['intrinsics'])
        voice = Voice.from_str[d['voice']]
        conj = Conjugation.from_str[d['conj']]
        is_split = d['is_split']
        relative_cont = RelativeContainment.from_str[d['relative_cont']]
        contract_not = d['contract_not']
        split_inf = d['split_inf']
        sbj_handling = SubjunctiveHandling.from_str[d['sbj_handling']]
        return SurfaceVerb(
            intrinsics, voice, conj, is_split, relative_cont, contract_not,
            split_inf, sbj_handling)
