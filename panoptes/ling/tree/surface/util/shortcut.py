from collections import defaultdict

from panoptes.etc.dicts import v2k_from_k2vv, v2kk_from_k2v
from panoptes.etc.enum import enum
from panoptes.ling.glue.grammatical_number import N2, nx_to_nx
from panoptes.ling.glue.inflection import N2_TO_CONJ
from panoptes.ling.glue.magic_token import PLACE_PREP, TIME_PREP
from panoptes.ling.tree.common.util.selector import Melange
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
        row = Melange.from_str[s]
        rows.append(row)
    assert set(rows) == Melange.values

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

    shs = set()
    for (melange, sh), (ss, is_archaic) in r.iteritems():
        shs.add(sh)
    assert shs == ShortcutColumn.values

    return r


class ShortcutManager(object):
    """
    Saying and parsing of shortcuts.
    """

    def __init__(self, count_restriction_checker):
        # CountRestrictionChecker.
        self.count_restriction_checker = count_restriction_checker

        # Melange, ShortcutColumn -> tokens, is_archaic.
        self.mel_sh2ss_archaic = make_shortcut_table()

        # Tokens, is_archaic -> list of (Melange, ShortcutColumn).
        self.ss_archaic2mels_shs = v2kk_from_k2v(self.mel_sh2ss_archaic)

        # noun -> shortcut columns.
        C = ShortcutColumn
        self.noun2shortcut_cols = defaultdict(list, {
            'person': [C.ONE, C.BODY],
            'thing': [C.THING],
            'place': [C.PLACE],
            'source': [C.SOURCE, C.SOURCE_FROM],
            'goal': [C.GOAL],
            'time': [C.TIME],
            'way': [C.WAY, C.WAY_BY],
            'reason': [C.REASON, C.REASON_FORE, C.REASON_LATIN],
        })

        self.noun2hallucinate_prep = {
            'place': PLACE_PREP,
            'time': TIME_PREP,
        }

        # shortcut column -> noun.
        self.shortcut_col2noun = v2k_from_k2vv(self.noun2shortcut_cols)

        # Correlative -> count restriction, grammatical number override.
        M = Melange
        R = CountRestriction
        self.melange2res_ogn = {
            M.INDEF:      (None,            None),
            M.DEF:        (None,            None),
            M.INTR:       (R.ALL_ONE,       None),
            M.PROX:       (R.ALL_ONE,       None),
            M.DIST:       (R.ALL_ONE,       None),
            M.EXIST:      (R.ONE_OF_PLURAL, None),
            M.ELECT_ANY:  (R.ONE_OF_PLURAL, None),
            M.ELECT_EVER: (R.ALL_ONE,       None),
            M.UNIV_EVERY: (R.ALL,           N2.SING),
            M.UNIV_ALL:   (R.ALL,           N2.SING),
            M.NEG:        (R.NONE,          N2.SING),
            M.ALT:        (R.ONE_OF_PLURAL, None),
        }

    def say(self, prep, n, of_n, melange, noun, allow_archaic):
        """
        args -> SayResult or None

        See if the args can expressed using a 'shortcut'.
        """
        # TODO: require and swallow prepositions correctly.

        restriction, override_gram_num = self.melange2res_ogn[melange]
        if not restriction:
            return None
        if not self.count_restriction_checker.is_possible(restriction, n, of_n):
            return None

        if override_gram_num:
            gram_num = override_gram_num
        else:
            gram_num = nx_to_nx(n, N2)
        conj = N2_TO_CONJ[gram_num]

        if allow_archaic:
            use_archaics = [False, True]
        else:
            use_archaics = [False]

        for use_archaic in use_archaics:
            for shortcut_col in self.noun2shortcut_cols[noun]:
                ss, is_archaic = self.mel_sh2ss_archaic[(melange, shortcut_col)]
                if is_archaic and not use_archaic:
                    continue

                # TODO: swallow preposition correctly.
                eat_prep = shortcut_col in \
                    (ShortcutColumn.PLACE, ShortcutColumn.TIME)

                return SayResult(tokens=list(ss), conjugation=conj,
                                 eat_prep=eat_prep)

        return None

    def parse(self, ss):
        """
        tokens -> list of (preposition, Correlative, noun, gram num override)
        """
        rr = []
        for is_archaic in [False, True]:
            for melange, shortcut_col in \
                    self.ss_archaic2mels_shs[(ss, is_archaic)]:
                noun = self.shortcut_col2noun[shortcut_col]
                _, gram_num_override = self.melange2res_ogn[melange]
                noun = self.noun2hallucinate_prep.get(noun)
                r = (prep, melange, noun, gram_num_override)
                rr.append(r)
        return rr
