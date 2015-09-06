from collections import defaultdict

from base.dicts import v2k_from_k2vv
from base.enum import enum
from ling.glue.correlative import SurfaceCorrelative


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
ELECT_EVER -            -           -          wherever   (whenceever)
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
ELECT_EVER -            (whithersoever) whenever    however
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


class ShortcutManager(object):
    """
    Saying and parsing of shortcuts.
    """

    def __init__(self, count_restriction_checker):
        # CountRestrictionChecker.
        self.count_restriction_checker = count_restriction_checker

        # SurfaceCorrelative, ShortcutColumn -> tokens, is_archaic.
        self.cor_sh2ss_archaic = make_shortcut_table()

        # Tokens, is_archaic -> SurfaceCorrelative, ShortcutColumn.
        self.ss_archaic2cors_shs = v2kk_from_k2v(self.cor_sh2ss_archaic)

        # thing -> shortcut columns.
        C = ShortcutColumn
        self.thing2shortcut_cols = defaultdict(list, {
            'person': [C.ONE, C.BODY],
            'thing': [C.THING],
            'place': [C.PLACE],
            'source': [C.SOURCE, C.SOURCE_FROM],
            'goal': [C.GOAL],
            'time': [C.TIME],
            'way': [C.WAY, C.WAY_BY],
            'reason': [C.REASON, C.REASON_FORE, C.REASON_LATIN],
        })

        # shortcut column -> thing.
        self.shortcut_col2thing = v2k_from_k2vv(self.thing2shortcut_cols)

        # Correlative -> count restriction, grammatical number override.
        C = SurfaceCorrelative
        R = CountRestriction
        self.cor2counts = {
            C.INDEF: (None, None),
            C.DEF: (None, None),
            C.INTR: (R.ALL_ONE, None),
            C.PROX: (R.ALL_ONE, None),
            C.DIST: (R.ALL_ONE, None),
            C.EXIST: (R.ONE_OF_N, None),
            C.ELECT_ANY: (R.ONE_OF_N, None),
            C.ELECT_EVER: (R.ALL_ONE, None),
            C.UNIV_EVERY: (R.ALL, N2.SING),
            C.UNIV_ALL: (R.ALL, N2.SING),
            C.NEG: (R.NONE, N2.SING),
            C.ALT: (R.ONE_OF_N, None),
        }

    def say(self, prep, n, of_n, cor, thing, allow_archaic):
        """
        args -> tokens or None

        See if the preposition and noun and can expressed using a 'shortcut'.
        """
        # TODO: require and swallow prepositions correctly.

        restriction = self.cor2counts[cor][0]
        if not restriction:
            return None
        if not self.count_restriction_checker.is_possible(restriction, n, of_n):
            return None

        if allow_archaic:
            use_archaics = [False, True]
        else:
            use_archaics = [False]

        for shortcut_col in self.thing2shortcut_cols[thing]:
            for use_archaic in use_archaics:
                ss, is_archaic = self.cor_sh2ss_archaic[(cor, shortcut_col)]
                if is_archaic and not use_archaic:
                    continue
                return ss

        return None

    def parse(self, ss):
        """
        tokens -> list of (preposition, correlative, thing, gram num override)
        """
        rr = []
        for is_archaic in [False, True]:
            for cor, shortcut_col in self.ss_archaic2cors_shs[(ss, is_archaic)]:
                thing = self.shortcut_col2thing[shortcut_col]
                gram_num_override = self.cor2counts[cor][1]
                r = (None, cor, thing, gram_num_override)
                rr.append(r)
        return rr