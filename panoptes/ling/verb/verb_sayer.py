from collections import defaultdict

from ling.verb.verb import ModalFlavor, Modality


Mood


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

    lines = text.strip().split('\n')
    flavor_cond2modals_moods = defaultdict(list)
    for line in lines:
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

        self.mood2tense2etense = make_mood2tense2etense()
