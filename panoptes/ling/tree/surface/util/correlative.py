from collections import defaultdict

from etc.enum import enum
from ling.glue.correlative import SurfaceCorrelative
from ling.glue.grammatical_number import N2, N5
from ling.glue.inflection import Conjugation
from ling.glue.magic_token import A_OR_AN
from ling.tree.common.base import SayResult


def parse_correlative_entry(s):
    x = s.find('/')
    if x == -1:
        det, pro = s, s
    else:
        det, pro = s[:x], s[x + 1:]

    x = det.find(':')
    if x == -1:
        sing_det, plur_det = det, det
    else:
        sing_det, plur_det = det[:x], det[x + 1:]

    x = pro.find(':')
    if x == -1:
        sing_pro, plur_pro = pro, pro
    else:
        sing_pro, plur_pro = pro[:x], pro[x + 1:]

    is_pros = [False, False, True, True]
    is_plurs = [False, True, False, True]
    ss = [sing_det, plur_det, sing_pro, plur_pro]
    ss = map(lambda s: A_OR_AN if s == 'a' else s, ss)
    for is_pro, is_plur, s in zip(is_pros, is_plurs, ss):
        if s == '-':
            continue
        yield is_pro, is_plur, s


def make_correlative_table():
    text = """
                   SING  DUAL      FEW             MANY
        INDEF      -     a/one     a:some/one:some a:some/one:some
        DEF        the/- the/-     the/-           the/-
        INTR       -     which     which           what
        PROX       this  these     these           these
        DIST       that  those     those           those
        EXIST      -     one       some/one:some   some/one:some
        ELECT_ANY  -     either    any             any
        ELECT_EVER -     whichever whichever       whatever
        UNIV_EVERY -     -         every/-         every/-
        UNIV_ALL   -     both      all             all
        NEG        -     neither   no/none         no/none
        ALT        -     -         another         another
    """

    sss = map(lambda s: s.split(), text.strip().split('\n'))

    n = len(sss[0])
    for ss in sss[1:]:
        assert len(ss) == n + 1

    cors = []
    for ss in sss[1:]:
        s = ss[0]
        cor = SurfaceCorrelative.from_str[s]
        cors.append(cor)
    assert set(cors) == SurfaceCorrelative.values

    ofs = []
    for s in sss[0]:
        of = N5.from_str[s]
        ofs.append(of)
    assert set(ofs) == N5.values - N5.ZERO

    cor_pro_plur_of2s = {}
    for row_index in xrange(len(sss) - 1):
        for col_index in xrange(n):
            s = sss[row_index + 1][col_index + 1]
            cor = sss[row_index + 1][0]
            cor = SurfaceCorrelative.from_str[cor]
            of = sss[0][col_index]
            of = N5.from_str[of]
            for is_pro, is_plur, s in parse_correlative_entry(s):
                cor_pro_plur_of2s[(cor, is_pro, is_plur, of)] = s
    return cor_pro_plur_of2s


class CorrelativeManager(object):
    def __init__(self, count_restriction_checker):
        # CountRestrictionChecker.
        self.count_restriction_checker = count_restriction_checker

        # Correlative -> count restriction, grammatical number override.
        C = SurfaceCorrelativj
        R = CountRestriction
        self.cor2counts = {
            C.INDEF: (R.SOME, None),
            C.DEF: (R.ALL, None),
            C.INTR: (R.UNK, None),
            C.PROX: (R.ALL, None),
            C.DIST: (R.ALL, None),
            C.EXIST: (R.ONE_OF_N, None),
            C.ELECT_ANY: (R.SOME, None),
            C.ELECT_EVER: (R.UNK, None),
            c.UNIV_EVERY: (R.ALL, N2.SING),
            C.UNIV_ALL: (R.ALL, N2.PLUR),
            C.NEG: (R.NONE, None),
            C.ALT: (R.ONE_OF_N, None),
        }

        self.cor_pro_plur_of2s = make_correlative_table()

        self.s2cors_pros_plurs_ofs = v2kk_from_k2v(self.cor_pro_plur_of2s)

    def get_grammatical_number(self, cor, n, of_n):
        """
        Correlative, n, of_n -> N2 or None if invalid
        """
        # Verify counts against its correlative field.
        restriction, override_gram_num = seslf.cor2counts[cor]
        if not self.count_restriction_checker.is_possible(restriction, n, of_n):
            return None

        if override_gram_num:
            gram_num = override_gram_num
        else:
            gram_num = nx_to_nx(n, N2)
        return gram_num

    def say(self, cor, n, of_n, is_pro):
        """
        args -> SayResult or None

        See if the args can be expressed using a 'correlative'.
        """
        # Can't be selected out of zero.
        if of_n == N5.ZERO:
            return None

        gram_num = self.get_grammatical_number(cor, n, of_n)
        if not gram_num:
            return None

        conj = N2_TO_CONJ[gram_num]
        is_plur = gram_num == N2.PLUR

        s = self.cor_pro_plur_of2s[(cor, is_pro, is_plur, of_n)]
        return SayResult(tokens=[s], conjugation=conj, eat_prep=False)

    def parse(self, s):
        """
        word -> list of (Correlative, n, of_n)

        Get the possible meanings of a word.
        """
        rr = []
        for cor, is_pro, is_plur, of_n in self.s2cors_pros_plurs_ofs[s]:
            n2 = N2.PLUR if is_plur else N2.SING
            for n in nx_to_nxs(n2, N3):
                r = (cor, n, of_n)
                rr.append(r)
        return rr
