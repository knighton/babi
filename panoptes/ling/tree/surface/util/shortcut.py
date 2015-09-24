from collections import defaultdict

from panoptes.etc.dicts import v2k_from_k2vv, v2kk_from_k2v
from panoptes.etc.enum import enum
from panoptes.ling.glue.grammatical_number import N2, nx_to_nx
from panoptes.ling.glue.inflection import N2_TO_CONJ
from panoptes.ling.glue.magic_token import PLACE_PREP, TIME_PREP
from panoptes.ling.tree.common.util.selector import Correlative
from panoptes.ling.tree.surface.base import SayResult
from panoptes.ling.tree.surface.util.count_restriction import CountRestriction


ShortcutColumn = enum("""ShortcutColumn =
    ONE BODY THING PLACE SOURCE SOURCE_FROM GOAL TIME WAY WAY_BY REASON
    REASON_FORE REASON_LATIN""")


def parse_partial(text):
    lines = text.strip().split('\n')
    sss = map(lambda line: line.split(), lines)

    n = len(sss[0])
    for ss in sss[1:]:
        assert len(ss) == n + 1

    rows = []
    for s in map(lambda ss: ss[0], sss[1:]):
        row = Correlative.from_str[s]
        rows.append(row)
    assert set(rows) == Correlative.values

    cols = []
    for s in sss[0]:
        col = ShortcutColumn.from_str[s]
        cols.append(col)

    mel_sh2ss_archaic = {}
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
            ss = tuple(s.split('_'))
            row = rows[row_index]
            col = cols[col_index]
            mel_sh2ss_archaic[(row, col)] = ss, is_archaic
    return mel_sh2ss_archaic


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
ELECT_EVER -            (whithersoever) whenever    however    -
UNIV_ALL   -            -               always      -          -
UNIV_EVERY -            -               (everywhen) (everyway) -
NEG        -            (nowhither)     never       (noway)    -
ALT        -            -               -           otherwise  -
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

    a = parse_partial(text_part_one)
    b = parse_partial(text_part_two)
    c = parse_partial(text_part_three)

    r = {}
    for k, v in a.iteritems():
        r[k] = v
    for k, v in b.iteritems():
        r[k] = v
    for k, v in c.iteritems():
        r[k] = v

    shortcut_cols = set()
    for (cor, sc), (ss, is_archaic) in r.iteritems():
        shortcut_cols.add(sc)
    assert shortcut_cols == ShortcutColumn.values

    return r


class ShortcutManager(object):
    """
    Saying and parsing of shortcuts.
    """

    def __init__(self):
        # Correlative, ShortcutColumn -> tokens, is_archaic.
        self.cor_sc2ss_archaic = make_shortcut_table()

        # Tokens, is_archaic -> list of (Correlative, ShortcutColumn).
        self.ss_archaic2cors_scs = v2kk_from_k2v(self.cor_sc2ss_archaic)

        # Noun -> preposition to hallucinate.
        self.noun2hallucinate_prep = {
            'place': PLACE_PREP,
            'time':  TIME_PREP,
        }

        # Correlative -> (count restriction if possible, grammatical number
        # override if any).
        C = Correlative
        CR = CountRestriction
        self.cor2res_ogn = {
            C.INDEF:      (None,             None),
            C.DEF:        (None,             None),
            C.INTR:       (CR.ALL_ONE,       None),
            C.PROX:       (CR.ALL_ONE,       None),
            C.DIST:       (CR.ALL_ONE,       None),
            C.EXIST:      (CR.ONE_OF_PLURAL, None),
            C.ELECT_ANY:  (CR.ONE_OF_PLURAL, None),
            C.ELECT_EVER: (CR.ALL_ONE,       None),
            C.UNIV_EVERY: (CR.ALL,           N2.SING),
            C.UNIV_ALL:   (CR.ALL,           N2.SING),
            C.NEG:        (CR.NONE,          N2.SING),
            C.ALT:        (CR.ONE_OF_PLURAL, None),
        }

        # Noun -> shortcut columns.
        C = ShortcutColumn
        self.noun2shortcut_cols = defaultdict(list, {
            'person': [C.ONE, C.BODY],
            'thing':  [C.THING],
            'place':  [C.PLACE],
            'source': [C.SOURCE, C.SOURCE_FROM],
            'goal':   [C.GOAL],
            'time':   [C.TIME],
            'way':    [C.WAY, C.WAY_BY],
            'reason': [C.REASON, C.REASON_FORE, C.REASON_LATIN],
        })

        # Shortcut column -> noun.
        self.shortcut_col2noun = v2k_from_k2vv(self.noun2shortcut_cols)

    def say(self, prep, selector, noun, allow_archaic):
        """
        args -> SayResult or None

        See if the args can be expressed using a 'shortcut' word.
        """
        n2 = selector.decide_n2(self.cor2res_gno)
        if not n2:
            return None

        conj = N2_TO_CONJ[n2]

        for shortcut_col in self.noun2shortcut_cols[noun]:
            key = (selector.correlative, shortcut_col)
            tokens, is_archaic = self.cor_sc2ss_archaic[key]
            tokens = list(tokens)

            if is_archaic and not allow_archaic:
                continue

            noun = self.shortcut_col2noun[shortcut_col]
            eat_prep = noun in self.noun2hallucinate_prep

            return SayResult(tokens=tokens, conjugation=conj, eat_prep=eat_prep)

        return None

    def parse(self, ss):
        """
        tokens -> list of (hallucinated preposition, Selector, noun)

        Try to pull a shortcut out of the given words (typically just one word).
        """
        rr = []
        for is_archaic in [False, True]:
            for correlative, shortcut_col in \
                    self.ss_archaic2cors_scs[(ss, is_archaic)]:
                noun = self.shortcut_col2noun[shortcut_col]
                prep = self.noun2hallucinate_prep.get(noun)
                count_res, _ = self.cor2res_ogn[correlative]
                selector = Selector.from_correlative(correlative, count_res)
                rr.append(prep, selector, noun)
        return rr
