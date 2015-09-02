from collections import defaultdict

from ling.verb.verb import ModalFlavor, Modality, VerbForm


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
    NORMAL_FINITE ZERO_RELCLAUSE_FINITE BARE_INF TO_INF GERUND""")


# Linguistic mood.
#
# IMP      imperative
# NORMAL   normal
# SBJ_IMP  subjunctive-imperative
# SBJ_CF   subjunctive-counterfactual
Mood = enums.new('Mood = NORMAL IMP SBJ_IMP SBJ_CF')


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


class VerbSayer(object):
    """
    SurfaceVerb -> words
    """

    def __init__(self):
        # (ModalFlavor, is conditional) -> list of (modal verb, mood).
        #
        # Does not include the indicative future exception ("will").
        self.normal_flavor_cond2modals_moods = \
            make_flavor_cond2modals_moods(known_modals)

        # Mood -> Tense -> EphemeralTense.
        self.mood2tense2etense = make_mood2tense2etense()

        # VerbForm -> EphemeralVerbForm.
        self.vf2evf = {
            VerbForm.FINITE:          EphemeralVerbForm.NORMAL_FINITE,
            VerbForm.BARE_INF:        EphemeralVerbForm.BARE_INF,
            VerbForm.TO_INF:          EphemeralVerbForm.TO_INF,
            VerbForm.GERUND:          EphemeralVerbForm.GERUND,
            VerbForm.SUBJLESS_GERUND: EphemeralVerbForm.GERUND,
        }

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
