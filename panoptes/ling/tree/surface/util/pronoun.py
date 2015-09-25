from collections import defaultdict
from copy import deepcopy

from panoptes.etc.dicts import v2kk_from_k2v
from panoptes.etc.enum import enum
from panoptes.ling.glue.grammatical_number import N2, N3, N5, nx_to_nx, \
    nx_to_nxs
from panoptes.ling.glue.inflection import Conjugation, N2_TO_CONJ
from panoptes.ling.glue.magic_token import A_OR_AN
from panoptes.ling.tree.common.util.selector import Correlative, \
    CountRestriction, Selector
from panoptes.ling.tree.surface.base import SayResult


def parse_det_pronoun_entry(s, of):
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

        if is_plur and of in (N5.ZERO, N5.SING):
            continue

        yield is_pro, is_plur, s


def make_det_pronoun_table():
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
        cor = Correlative.from_str[s]
        cors.append(cor)
    assert set(cors) == Correlative.values

    ofs = []
    for s in sss[0]:
        of = N5.from_str[s]
        ofs.append(of)
    assert set(ofs) == N5.values - set([N5.ZERO])

    cor_pro_plur_of2s = {}
    for row_index in xrange(len(sss) - 1):
        for col_index in xrange(n):
            s = sss[row_index + 1][col_index + 1]
            cor = sss[row_index + 1][0]
            cor = Correlative.from_str[cor]
            of = sss[0][col_index]
            of = N5.from_str[of]

            for is_pro, is_plur, s in parse_det_pronoun_entry(s, of):
                cor_pro_plur_of2s[(cor, is_pro, is_plur, of)] = s
    return cor_pro_plur_of2s


def split_into_ranges(nn):
    if not nn:
        return []

    rr = []
    begin_n = nn[0]
    end_n = nn[0]
    for n in nn[1:]:
        if end_n + 1 < n:
            rr.append((begin_n, end_n))
            begin_n = n
        end_n = n
    rr.append((begin_n, end_n))
    return rr


assert split_into_ranges([]) == []
assert split_into_ranges([0]) == [(0, 0)]
assert split_into_ranges([1]) == [(1, 1)]
assert split_into_ranges([0, 1, 2]) == [(0, 2)]
assert split_into_ranges([0, 2]) == [(0, 0), (2, 2)]
assert split_into_ranges([0, 2, 4, 5]) == [(0, 0), (2, 2), (4, 5)]


def combine_entries(aaa, cor2res_gno):
    """
    list of (Correlative, is pro, is plur, out of) -> (Selectors, Selectors)
    """
    # They are all the same Correlative except for "some" (INDEF + EXIST).
    cor_pro2ns_ofs = defaultdict(list)
    for correlative, is_pro, is_plur, of in aaa:
        if is_plur:
            nn = [N5.ZERO, N5.DUAL, N5.FEW, N5.MANY]
        else:
            nn = [N5.SING]
        nn = filter(lambda n: n <= of, nn)
        for n in nn:
            cor_pro2ns_ofs[(correlative, is_pro)].append((n, of))

    # For each grouping,
    dets = []
    pros = []
    for correlative, is_pro in sorted(cor_pro2ns_ofs):
        ns_ofs = cor_pro2ns_ofs[(correlative, is_pro)]

        # Collect the variety of how many/out of there are for this word.
        ns, ofs = map(set, zip(*ns_ofs))

        # Require that each out-of range is contiguous.  This is also because it
        # happens to be true and it allows Selectors to contain ranges instead
        # of the insanity of individual N5s.
        ofs = sorted(ofs)
        assert ofs == range(ofs[0], ofs[-1] + 1)

        for n_min, n_max in split_into_ranges(sorted(ns)):
            # Get the possible range of how many they were selected from.
            of_n_min = min(ofs)
            of_n_max = max(ofs)

            # Create a Selector that covers all of those tuples.
            r = Selector(correlative, n_min, n_max, of_n_min, of_n_max)
            count_restriction, _ = cor2res_gno[correlative]
            r = r.fitted_to_count_restriction(count_restriction)
            if not r:
                continue

            if is_pro:
                pros.append(r)
            else:
                dets.append(r)

    return dets, pros


class DetPronounManager(object):
    def __init__(self):
        # Correlative -> count restriction, grammatical number override.
        C = Correlative
        R = CountRestriction
        self.cor2res_gno = {
            C.INDEF:      (R.SOME,          None),
            C.DEF:        (R.ALL,           None),
            C.INTR:       (R.ANY,           None),
            C.PROX:       (R.ALL,           None),
            C.DIST:       (R.ALL,           None),
            C.EXIST:      (R.ONE_OF_PLURAL, None),
            C.ELECT_ANY:  (R.SOME,          None),
            C.ELECT_EVER: (R.ANY,           None),
            C.UNIV_EVERY: (R.ALL,           N2.SING),
            C.UNIV_ALL:   (R.ALL,           N2.PLUR),
            C.NEG:        (R.NONE,          None),
            C.ALT:        (R.ONE_OF_PLURAL, None),
        }

        # (Correlative, is pronoun, is plural, out of N5) -> word.
        self.cor_pro_plur_of2s = make_det_pronoun_table()

        # Word -> list of Selectors.
        self.determiner2selectors = defaultdict(list)
        self.pronoun2selectors = defaultdict(list)
        s2cors_pros_plurs_ofs = v2kk_from_k2v(self.cor_pro_plur_of2s)
        for s, aaa in s2cors_pros_plurs_ofs.iteritems():
            dets, pros = combine_entries(aaa, self.cor2res_gno)
            self.determiner2selectors[s] = dets
            self.pronoun2selectors[s] = pros

    def show(self):
        print '-' * 80
        print 'DetPronounManager'
        print
        for cor, is_pro, is_plur, of_n in sorted(self.cor_pro_plur_of2s):
            s = self.cor_pro_plur_of2s[(cor, is_pro, is_plur, of_n)]
            print '*', Correlative.to_str[cor], is_pro, is_plur, \
                N5.to_str[of_n], s
        print '-' * 80

    def say(self, selector, is_pro):
        """
        Selector, whether pronoun or determiner -> SayResult or None

        See if the args can be said using a determiner or (impersonal) pronoun.
        """
        is_plur = True if selector.guess_n(N2) == N2.PLUR else False
        key = (selector.correlative, is_pro, is_plur, selector.guess_of_n(N5))
        s = self.cor_pro_plur_of2s.get(key)
        if not s:
            return None

        n2 = selector.decide_grammatical_number(self.cor2res_gno)
        if not n2:
            return None
        conj = N2_TO_CONJ[n2]

        return SayResult(tokens=[s], conjugation=conj, eat_prep=False)

    def say_determiner(self, selector):
        return self.say(selector, False)

    def say_pronoun(self, selector):
        return self.say(selector, True)

    def parse_determiner(self, s):
        """
        word -> list of Selectors
        """
        rr = self.determiner2selectors[s]
        return deepcopy(rr)

    def parse_pronoun(self, s):
        """
        word -> list of Selectors
        """
        rr = self.pronoun2selectors[s]
        return deepcopy(rr)
