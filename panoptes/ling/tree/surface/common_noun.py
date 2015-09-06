from collections import defaultdict

from base.dicts import v2k_from_k2vv
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


SurfaceCorrelative = enum("""SurfaceCorrelative =
    INDEF DEF INTR PROX DIST EXIST ELECT_ANY ELECT_EVER UNIV_ALL UNIV_EVERY NEG
    ALT""")


ShortcutColumn = enum("""ShortcutColumn =
    ONE BODY THING PLACE SOURCE SOURCE_FROM GOAL TIME WAY REASON REASON_FORE
    REASON_LATIN""")


def make_shortcut_table():
    text_part_one = """
           ONE          BODY        THING      PLACE      SOURCE
INDEF      -            -           -          -          -
DEF        -            -           -          -          -
INTR       X            X           X          where      (whence)
PROX       -            -           -          here       (hence)
DIST       -            -           -          there      (thence)
EXIST      someone      somebody    something  somewhere  -
ELECT_ANY  anyone       anybody     anything   anywhere   -
ELECT_EVER X            X           X          wherever   (whenceever)
UNIV_ALL   -            -           -          -          -
UNIV_EVERY everyone     everybody   everything everywhere -
NEG        no_one       nobody      nothing    nowhere    (nowhence)
ALT        -            -           -          elsewhere  -
    """

    text_part_two = """
           SOURCE_FROM  GOAL            TIME        WAY        WAY_BY
INDEF      -            -               -           -          -
DEF        -            -               -           -          -
INTR       (whencefrom) (whither)       when        how        -
PROX       -            (hither)        now         thus       hereby
DIST       (thencefrom) (thither)       then        -          thereby
EXIST      -            (somewhither)   sometime    somehow    -
ELECT_ANY  -            (anywhither)    anytime     -          -
ELECT_EVER -            (whithersoever) whenver     however
UNIV_ALL   -            -               always      -
UNIV_EVERY -            -               (everywhen) (everyway)
NEG        -            (nowhither)     never       (noway)
ALT        -            -               -           otherwise
    """

    text_part_three = """
           REASON    REASON_FORE REASON_LATIN
INDEF      -         -           -
DEF        -         -           -
INTR       why       (wherefore) -
PROX       thus      -           -
DIST       -         therefore   ergo
EXIST      -         -           -
ELECT_ANY  -         -           -
ELECT_EVER -         -           -
UNIV_ALL   -         -           -
UNIV_EVERY -         -           -
NEG        -         -           -
ALT        -         -           -
    """

    aa = text_part_one.strip().split('\n')
    bb = text_part_one.strip().split('\n')
    cc = text_part_one.strip().split('\n')
    lines = map(lambda (a, b, c): a + b + c, zip(aa, bb, cc))
    sss = map(lambda line: line.split(), lines)

    n = len(sss[0])
    for ss in sss[1:]:
        assert len(ss) == n + 1

    rows = []
    for s in map(lambda ss: ss[0], sss[1:]):
        row = SurfaceCorrelative.from_str[s]
        rows.append(row)
    assert set(rows) == SurfaceCorrelative.values

    cols = []
    for s in sss[0][1:]:
        col = ShortcutColumn.from_str[s]
        cols.append(col)
    assert set(cols) == ShortcutColumn.values

    cor_sh2ss_archaic = {}
    for row_index in xrange(len(sss) - 1):
        for col_index in xrange(n):
            s = sss[row_index + 1][col_index + 1]
            if s == '-' or s == 'X':
                continue
            if s.startswith('(') and s.endswith(')'):
                s = s[1:-1]
                is_archaic = True
            else:
                is_archaic = False
            ss = tuple(ss.split('_'))
            row = rows[row_index]
            col = cols[col_index]
            cor_sh2ss_archaic[(row, col)] = ss, is_archaic
    return cor_sh2ss_archaic


class ShortcutKnowledge(object):
    def __init__(self):
        # SurfaceCorrelative, ShortcutColumn -> tokens, is_archaic.
        self.cor_sh2ss_archaic = make_shortcut_table()

        # Tokens, is_archaic -> SurfaceCorrelative, ShortcutColumn.
        self.ss_archaic2cors_shs = v2kk_from_k2v(self.cor_sh2ss_archaic)

        self.thing2shortcut_cols = defaultdict(list, {
            'person': [ShortcutColumn.ONE, ShortColumn.BODY],
            'thing': [ShortcutColumn.THING],
            'place': [ShortcutColumn.PLACE],
            'source': [ShortcutColumn.SOURCE, ShortcutColumn.SOURCE_FROM],
            'goal': [ShortcutColumn.GOAL],
            'time': [ShortcutColumn.TIME],
            'way': [ShortcutColumn.WAY, ShortcutColumn.WAY_BY],
            'reason': [ShortcutColumn.REASON, ShortcutColumn.REASON_FORE,
                       ShortcutColumn.REASON_LATIN],
        })

        self.shortcut_col2thing = v2k_from_k2vv(self.thing2shortcut_cols)

    def say(self, prep, cor, thing, allow_archaic):
        """
        preposition, correlative, thing, allow archaic -> tokens or None

        See if the preposition and noun and can expressed using a 'shortcut'.
        """
        # TODO: require and swallow prepositions correctly.

        if allow_archaic:
            use_archaics = [False, True]
        else:
            use_archaics = [False]

        for use_archaic in use_archaics:
            for shortcut_col in self.thing2shortcut_cols[thing]:
                ss, is_archaic = self.cor_sh2ss_archaic[(cor, shortcut_col)]
                if is_archaic and not use_archaic:
                    continue
                return ss

        return None

    def parse(self, ss):
        """
        tokens -> list of (preposition, correlative, thing)
        """
        rr = []
        for is_archaic in [False, True]:
            for cor, shortcut_col in self.ss_archaic2cors_shs[(ss, is_archaic)]:
                thing = self.shortcut_col2thing[shortcut_col]
                r = (None, cor, thing)
                rr.append(r)
        return rr
