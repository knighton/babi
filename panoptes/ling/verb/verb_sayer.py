from collections import defaultdict

from ling.glue.inflection import CONJ2INDEX, Conjugation
from ling.verb.annotation import annotate_as_pro_verb
from ling.verb.conjugation import Conjugator
from ling.verb.verb import ModalFlavor, Modality, SurfaceVerb, VerbForm, Voice


# Whether.
#
# Like polarity, but also "does" in "she *does* know!").
#
# NO    no
# YES   yes
# EMPH  emphatic yes (yes + you were expecting no)
Whether = enums.new('Whether = NO YES EMPH')


# Ephemeral tense.
#
# Gotcha warning: it is loosely related to time.
#
# PAST      past
# NONPAST   present and future (+ will)
# SBJ_PAST  past subjunctive
# SBJ_PRES  present subjunctive
# SBJ_FUT   future subjunctive
EphemeralTense = enums.new(
    'EphemeralTense = PAST NONPAST SBJ_PAST SBJ_PRES SBJ_FUT')


# Ephemeral verb form.
#
# Distinguishes finites that are in zero-relative pronoun relative clauses
# (this matters for saying/parsing).
EphemeralVerbForm = enums.new("""EphemeralVerbForm =
    NORMAL_FINITE ZERO_REL_CLAUSE_FINITE BARE_INF TO_INF GERUND""")


# Ephemeral verb form -> whether finite.
EPHEMERAL_VERB_FORM2IS_FINITE = {
    EphemeralVerbForm.NORMAL_FINITE: True,
    EphemeralVerbForm.ZERO_REL_CLAUSE_FINITE: True,
    EphemeralVerbForm.BARE_INF: False,
    EphemeralVerbForm.TO_INF: False,
    EphemeralVerbForm.GERUND: False,
}


# Linguistic mood.
#
# IMP      imperative
# NORMAL   normal
# SBJ_IMP  subjunctive-imperative
# SBJ_CF   subjunctive-counterfactual
Mood = enums.new('Mood = NORMAL IMP SBJ_IMP SBJ_CF')


# Mood -> list of possible EphemeralTenses.
MOOD2VALID_ETENSES = {
    Mood.NORMAL: [EphemeralTense.PAST, EphemeralTense.NONPAST],
    Mood.SBJ_CF: [EphemeralTense.SBJ_PAST, EphemeralTense.SBJ_FUT],
    Mood.SBJ_IMP: [EphemeralTense.SBJ_PRES],
    Mood.IMP: [EphemeralTense.NONPAST],
}


class EphemeralVerb(object):
    """
    Ephemeral structure created during the process of saying verbs.

    This exists in order to capture all the quirkiness of English so
    surface/deep structure doesn't have to deal with it.

    Note that some combinations of fields are invalid, which will be discovered
    during saying.
    """

    def __init__(self, lemma, whether, modal, voice, tense, aspect, mood, conj,
                 verb_form, split_inf, use_were_sbj):
        self.lemma = lemma
        assert self.lemma
        assert isinstance(self.lemma, str)

        self.whether = whether
        assert Whether.is_valid(self.whether)

        if self.modal is not None:
            assert self.modal
            assert isinstance(self.modal, str)

        self.voice = voice
        assert Voice.is_valid(self.voice)

        self.tense = tense
        assert EphemeralTense.is_valid(tense)

        self.aspect = aspect
        assert isinstance(self.aspect, Aspect)

        self.mood = mood
        assert Mood.is_valid(self.mood)

        self.conj = conj
        assert Conjugation.is_valid(self.conj)

        self.verb_form = verb_form
        assert EphemeralVerbForm.is_valid(self.verb_form)

        self.split_inf = split_inf
        assert isinstance(self.split_inf, bool)

        self.use_were_sbj = use_were_sbj
        assert isinstance(self.use_were_sbj, bool)


def make_flavor_cond2modals_moods(known_modals):
    text = """
        MODALITY        NORMAL  CONDITIONAL
        INDICATIVE      NORMAL  would
        SUBJUNCTIVE_CF  SBJ_CF  -

        DEDUCTIVE       must    -
        ALMOST_CERTAIN  must    -
        PROBABLE        should  -
        POSSIBLE        can,may could,might

        IMPERATIVE      IMP     -
        SUBJUNCTIVE_IMP SBJ_IMP -
        ABILITY         can     could
        PERMISSIVE      may,can could
        NORMATIVE       should  -
        NECESSITY       must    -
    """

    flavor_cond2modals_moods = defaultdict(list)
    for line in text.strip().split('\n')
        flavor, normal, cond = line.split()
        flavor = ModalFlavor.from_str[flavor]
        for options, is_cond in ((normal, False), (cond, True)):
            if options == '-':
                options = []
            else:
                options = options.split(',')
            for text in options:
                mood = Mood.from_str.get(text)
                if mood:
                    modal = None
                else:
                    modal = text
                    assert modal in known_modals 
                    mood = Mood.NORMAL
                key = (flavor, is_cond)
                flavor_cond2modals_moods[key].append((modal, mood))

    r_flavors = set(map(lambda (m, _): m, r.iterkeys()))
    assert r_flavors == ModalFlavor.values

    return r


def make_mood2tense2etense():
    mood2etenses = {
        Mood.NORMAL: [
            EphemeralTense.PAST,
            EphemeralTense.NONPAST,
            EphemeralTense.NONPAST,
        ],
        Mood.IMP:
            [EmphemeralTense.NONPAST] * 3,
        Mood.SBJ_IMP:
            [EphemeralTense.SBJ_PRES] * 3,
        Mood.SBJ_CF: [
            EphemeralTense.SBJ_PAST,
            EphemeralTense.SBJ_PAST,
            EphemeralTense.SBJ_FUT
        ],
    }

    mood2tense2etense = {}
    for mood, etenses in mood2etenses.iteritems():
        mood2tense2etenses[mood] = dict(zip(
            [Tense.PAST, Tense.PRESENT, Tense.FUTURE],
            etenses))

    return mood2tense2etense


class VerbConfigError(Exception):
    """
    Raised when some combination of verb fields is not valid (individual fields
    are checked with assertions).

    When generating a lookup table by permuting all combinations of field
    values, catch and drop these exceptions.

    Outside of that, this error will never be encountered in correct code.
    """
    pass


class VerbEphemeralizer(object):
    """
    Converts SurfaceVerb to EphemeralVerb for saying.
    """

    def __init__(self):
        # VerbForm -> EphemeralVerbForm.
        #
        # Only for when not in a relative clause.
        self.nonrel_verbform2everbform = {
            VerbForm.FINITE:          EphemeralVerbForm.NORMAL_FINITE,
            VerbForm.BARE_INF:        EphemeralVerbForm.BARE_INF,
            VerbForm.TO_INF:          EphemeralVerbForm.TO_INF,
            VerbForm.GERUND:          EphemeralVerbForm.GERUND,
            VerbForm.SUBJLESS_GERUND: EphemeralVerbForm.GERUND,
        }

        # (ModalFlavor, is conditional) -> list of (modal verb, mood).
        #
        # Does not include the indicative future exception ("will").
        self.normal_flavor_cond2modals_moods = \
            make_flavor_cond2modals_moods(known_modals)

        # Mood -> Tense -> EphemeralTense.
        self.mood2tense2etense = make_mood2tense2etense()

    def everbform_from_verbform_relcont(self, verb_form, rel_cont):
        in_relative_clause = rel_cont != RelativeContainment.NOT_REL
        is_finite = verb_form == VerbForm.FINITE
        if in_relative_clause and not is_finite:
            raise VerbConfigError('Relative clause verbs must be finite')

        if rel_cont == RelativeContainment.ZERO:
            r = EphemeralVerbForm.ZERO_REL_CLAUSE_FINITE
        elif rel_cont == RelativeContainment.WORD:
            r = EphemeralVerbForm.NORMAL_FINITE
        elif rel_cont == RelativeContainment.NOT_REL:
            r = self.nonrel_verbform2everbform[verb_form]
        else:
            assert False

    def moods_modals_etenses_from_flavor_cond_tense(
            self, modal_flavor, is_cond, tense):
        """
        ModalFlavor, is_cond, Tense -> yields (Mood, modal, EphemeralTense).
        """
        # Get modal/mood options.
        #
        # Some combinations are invalid (the dashes in the table).  For example,
        # conditionality is not very common, so use "if <ind> then <non-cond>"
        # instead of "if <sbj-cf> then <cond>".
        key = (modal_flavor, is_cond)
        modal_moods = self.normal_flavor_cond2modals_moods.get(key)
        if not modals_moods:
            raise VerbConfigError(
                'There is no conditional form of the modality you have chosen')

        # We prefer the first one.
        for modal, mood in modals_moods:
            # Handle exceptions.
            if modal_flavor == ModalFlavor.INDICATIVE and tense == Tense.FUTURE:
                modal = 'will'

            # Get ephemeral tense.
            etense = self.mood2tense2etense[mood][tense]

            yield mood, modal, etense

    def convert(self, v, ignore_invalid_configs=False):
        """
        SurfaceVerb -> yields EphemeralVerb
        """
        assert isinstance(v, SurfaceVerb)
        v.check(allow_wildcards=False)

        if v.is_split and v.intrinsics.verb_form != VerbForm.FINITE and \
                not ignore_invalid_configs:
            raise VerbConfigError('Can only split words of finite verbs')

        # Polarity, etc. -> Whether.
        if v.intrinsics.polarity.tf:
            # "No, she *does* write."
            if v.intrinsics.polarity.is_contrary:
                w = Whether.EMPH

            # "Does she write?"
            elif v.is_split:
                w = Whether.EMPH

            # "Yes, she does."
            elif v.intrinsics.is_pro_verb:
                w = Whether.EMPH

            # "She writes."
            else:
                w = Whether.YES
        else:
            # "She doesn't write."
            w = Whether.NO
        whether = w

        # VerbForm, RelativeContainment -> EphemeralVerbForm.
        ephemeral_verb_form = \
            self.everbform_from_verbform_relcont(
                v.instrincs.verb_form, v.rel_cont)

        for mood, modal, ephemeral_tense in \
            self.moods_modals_etenses_from_flavor_cond_tense(
                v.intrinsics.modality.flavor, v.intrinsics.modality.is_cond,
                v.intrinsics.tense):
            use_were_sbj = v.sbj_handling == SubjunctiveHandling.WERE_SBJ
            yield EphemeralVerb(
                v.intrinsics.lemma, whether, modal, v.voice, ephemeral_tense,
                aspect, mood, v.conj, ephemeral_verb_form, v.split_inf,
                use_were_sbj)


def make_modal2indtense2mstr_perf():
    text = """
        MODAL  PAST        NONPAST
        can    could       can
        could  could_have  could
        may    may_have    may
        might  might_have  might
        should should_have should
        must   must_have   must
        will   would       will
        would  would_have  would
    """

    modal2indtense2mstr_perf = {}
    for line in text.strip().split('\n'):
        modal, past, nonpast_modal = line.split()

        assert modal.islower()

        ss = past.split('_')
        if len(ss) == 1:
            past_modal, have = past, False
        elif len(ss) == 2:
            past_modal, have = ss[0], True
            assert ss[1] == 'have'
        else:
            assert False

        assert nonpast_modal.islower()

        modal2indtense2mstr_perf[modal] = {
            EphemeralTense.PAST: (past_modal, have),
            EphemeralTense.NONPAST: (nonpast_modal, have),
        }

    return modal2indtense2mstr_perf


class EphemeralSayer(object):
    def __init__(self, conjugator):
        self.conjugator = conjugator

        # Modal -> indicative EphemeralTense -> (modal, is perf).
        self.modal2indtense2mstr_perf = make_modal2indtense2mstr_perf()

        # Keep auxiliaries around for quick access.
        self.to_be = self.create_verb('be')
        self.to_have_aux = self.create_verb('have').annotated_as_aux()
        self.to_do = self.create_verb('do')

    def check(self, v):
        # Modality is handled as either a mood or a modal verb, the other being
        # set to the default.
        if v.modal and v.mood != Mood.NORMAL:
            raise VerbConfigError('Cannot use both a modal verb and a mood')

        # Imperatives are second-person only.
        if v.mood == Mood.IMP and \
                v.conj not in (Conjugation.S2, Conjugation.P2):
            raise VerbConfigError('Imperatives are second-person only')

        # Check that the partially mood-specific EphemeralTense works with mood.
        if v.tense not in MOOD2VALID_ETENSES[v.mood]:
            raise VerbConfigError('Mood and ephemeral tense do not jive')

        # Note: there are probably a number of verbs that have similar meanings/
        # functions as modals and thereby can't logically be used as imperatives
        # (eg, "Ought to do that!"), but there's no nice way to check for that.

        # If verb is non-finite, only default mood/modal is allowed.
        if not EPHEMERAL_VERB_FORM2IS_FINITE[v.verb_form]:
            if v.modal:
                raise VerbConfigError('Non-finite verbs cannot use modals')

            if v.mood != Mood.NORMAL:
                raise VerbConfigError(
                    'Non-finite verbs must have indicative mood')

        # Zero means passive (eg, "the dog [walked] by me is here")
        if v.verb_form == EphemeralVerbForm.ZERO_REL_CLAUSE_FINITE and \
                v.voice != Voice.PASSIVE:
            raise VerbConfigError(
                'Relative clauses with the zero relative pronoun must be '
                'passive')

    def say(self, v):
        assert isinstance(v, EphemeralVerb)
        self.check(v)

        # Reason for hallucinate_is_perf:
        #
        # Typically, you use conjugation to tell past tense (eg, "go" ->
        # "went").  But if there's a modal in front, there goes your opportunity
        # to tell past tense that way.  So instead you say it as perfective
        # (regardless of whether it is actually perfective or not).
        #
        # Get the actually said forms of modals, and whether to hallucinate
        # perfective.  Eg, "I go" -> "I should go", but "I went" -> "I should
        # have gone".
        if v.modal and v.tense in (EphemeralTense.PAST, EphemeralTense.NONPAST):
            actual_modal, hallucinate_is_perf = \
                self.modal2indtense2mstr_perf[v.modal][v.tense]
        else:
            actual_modal, hallucinate_is_perf = v.modal, False
        use_perf = hallucinate_is_perf or v.aspect.is_perf

        # Get the conjugation plan for the verb.
        to_verb = self.conjugator.create_verb(v.lemma)

        # List the verb conjugation mappings to pick the correct forms of.
        rr = []
        if actual_modal:
            rr.append(actual_modal)
        if use_perf:
            rr.append(self.to_have_aux)
        if v.aspect.is_prog:
            rr.append(self.to_be)
        if v.voice == Voice.PASSIVE:
            rr.apepnd(self.to_be)
        rr.append(to_verb)

        if v.mood == Mood.SBJ_CF and v.tense == EphemeralTense.SBJ_FUT:
            # SBJ_CF future uses the "to be" future, unlike anything else below,
            # we do it separately up here.
            said_conj = Conjugation.P2 if v.use_were_sbj else v.conj
            were_or_was = self.to_be.past[CONJ2INDEX[said_conj]]
            rr = [were_or_was, 'to'] + rr

            if v.whether == Whether.NO:
                notx = 2 if v.split_inf else 1
                rr = rr[:notx] + ['not'] + rr[notx:]
        else:
            is_finite = EPHEMERAL_VERB_FORM2IS_FINITE[v.verb_form]

            # Add "do".
            if is_finite:
                if v.whether in (Whether.NO, Whether.EMPH):
                    mood_ok = v.mood == Mood.NORMAL
                    already_has_an_aux = \
                        actual_modal or use_perf or v.aspect.is_prog
                    can_use_do = \
                        to_verb.has_do_support and voice == Voice.ACTIVE
                    if mood_ok and not already_has_an_aux and can_use_do:
                        rr = [self.to_do] + rr

            # Add "to".
            if v.verb_form == EphemeralVerbForm.TO_INF:
                rr = ['to'] + rr

            # Add "not".
            if v.whether == Whether.NO:
                # Decide where to correctly put the 'not'.
                if is_finite:
                    if v.mood in (Mood.NORMAL, Mood.SBJ_CF):
                        notx = 1
                    else:
                        notx = 0
                else:
                    if v.verb_form == EphemeralVerbForm.TO_INF:
                        notx = 1 if v.split_inf else 0
                    else:
                        notx = 0

                # Actually insert it.
                rr = rr[:notx] + ['not'] + rr[notx:]

        # Conjugate the front word depending on mood, tense, etc., if it isn't a
        # modal, 'not', 'to', etc.  Leftovers are automatically converted to
        # their lemmas, so in a few cases we just do nothing.
        if is_finite:
            if v.mood == Mood.NORMAL:
                conjx = 0  # If there is a not, it's at index 1.
                if not isinstance(rr[conjx], str):
                    if v.tense == EphemeralTense.NONPAST:
                        rr[0] = rr[0].nonpast[CONJ2INDEX[v.conj]]
                    elif v.tense == EphemeralTense.PAST:
                        rr[0] = rr[0].past[CONJ2INDEX[v.conj]]
                    else:
                        assert False
            elif v.mood == Mood.SBJ_CF:
                if v.tense == EphemeralTense.SBJ_PAST:
                    said_conj = Conjugation.P2 if v.use_were_sbj else v.conj
                    rr[0] = rr[0].past[CONJ2INDEX[said_conj]]
                else:
                    # SBJ_FUT (the other option) is covered separately above.
                    assert False
            else:
                # IMP, SBJ_IMP.
                pass
        else:
            if v.verb_form == EphemeralVerbForm.GERUND:
                conjx = 1 if v.whether == Whether.NO else 0
                rr[conjx] = rr[conjx].pres_part

        # Index of end of infinitives (exclusive).
        z = len(rr)

        # If passive voice, use past participle of the last verb.
        if v.voice == Voice.PASSIVE:
            z -= 1
            zz[z] = rr[z].past_part

        # Conjugate for aspect on the preceding words, if applicable.
        if v.aspect.is_prog:
            z -= 1
            rr[z] = rr[z].pres_part

        if use_perf:
            z -= 1
            rr[z] = rr[z].past_part

        # The remaining verb words in the middle are left in lemma form.
        for x in range(0, z):
            if not isinstance(rr[x], str):
                rr[x] = rr[x].lemma

        # Finally, there are two types of finite.  Make modifications for the
        # weird kind of finite if necessary, involving dropping leading 'to be'
        # forms when inside relative clauses with the zero relative pronoun, eg.
        #   "the cat that [was seen] by you"
        # vs
        #   "the cat [seen] by you"
        if v.verb_form == EphemeralVerbForm.ZERO_REL_CLAUSE_FINITE:
            if rr[0] in ('is', 'are', 'was', 'were'):  # So passive voice.
                rr = rr[1:]

        return rr


def slice_verb_words(v, ss):
    """
    SurfaceVerb, joined words -> pre words, main words

    Determine where to split the verb words and where to end if pro-verb.

    Normal:          "[don't] you [like] apples?"  "i [don't like] apples."
    Pro-verbs:       "[have] you [not]?"  "[are n't] you?"
    Not-contraction: "[do] you [not like] it?" vs "[do n't] you [like] it?"
    """

    # Some non-finite cases.
    # Eg, "she requests that you [not come]".
    not_at_0 = 1 <= len(ss) and ss[0] == 'not'

    # Normal 'not' cases.
    # Eg, "i [do not like] you".
    not_at_1 = 2 <= len(ss) and ss[1] == 'not'

    # Future subjunctive 'not' cases.
    # Eg, "if you [were to not go]".
    not_at_2 = 3 <= len(ss) and ss[2] == 'not'

    # There can be at most one "not".
    assert sum([not_at_0, not_at_1, not_at_2]) in (0, 1)

    # Determine pre-words ("do" of "[do] you [not like]").
    if v.is_split:
        if not_at_1:
            i = 2 if v.contract_not else 1
        else:
            i = 1  # "Not" at 0 or 2, or not present.
    else:
        i = 0

    # Determine rest-words ("not like" in "[do] you [not like]").
    if v.intrinsics.is_pro_verb:
        if not_at_0:
            z = 1
        elif not_at_1:
            z = 2
        elif not_at_2:
            z = 3
        else:
            assert 'not' not in ss[2:]
            z = 1
    else:
        z = len(ss)

    # Get the ranges.
    a, b = ss[:i], ss[i:z]

    # If it's a pro-verb, mark the words as pro-verb words.
    if v.intrinsics.is_pro_verb:
        a = map(annotate_as_pro_verb, a)
        b = map(annotate_as_pro_verb, b)

    return a, b


class VerbSayer(object):
    def __init__(self):
        self.verb_ephemeralizer = VerbEphemeralizer()

        self.conjugator = Conjugator()
        self.ephemeral_sayer = EphemeralSayer(conjugator)

    def say(self, v):
        assert isinstance(v, SurfaceVerb)
        for ev in self.ephemeralizer.convert(v, ignore_invalid_configs=False):
            ss = self.ephemeral_sayer.say(ev)
            return slice_verb_words(v, ss)
        raise VerbConfigError('No say options found for verb')

    def get_all_say_options(self, v):
        assert isinstance(v, SurfaceVerb)
        for ev in self.ephemeralizer.convert(v, ignore_invalid_configs=True):
            try:
                ss = self.ephemeral_sayer.say(ev)
            except VerbConfigError:
                pass
            yield slice_verb_words(v, ss)
