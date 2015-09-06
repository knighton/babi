from collections import defaultdict

from base.enum import enum
from ling.glue.correlative import SurfaceCorrelative
from ling.glue.grammatical_number import N2, N5
from ling.glue.magic_token import A_OR_AN


def parse_det_pro_entry(s):
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


def make_det_pro_table():
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

    cor_pro_plur_of2ss = defaultdict(list)
    for row_index in xrange(len(sss) - 1):
        for col_index in xrange(n):
            s = sss[row_index + 1][col_index + 1]
            cor = sss[row_index + 1][0]
            cor = SurfaceCorrelative.from_str[cor]
            of = sss[0][col_index]
            of = N5.from_str[of]
            for is_pro, is_plur, s in parse_det_pro_entry(s):
                cor_pro_plur_of2ss[(cor, is_pro, is_plur, of)].append(s)
    return cor_pro_plur_of2ss


CountRequirement = enum("""CountRequirement =
    UNK NONE ONE_OF_N SOME ALL_ONE ALL""")


def parse_count_req_entry(s):
    if s == '-':
        return

    x = s.find('/')
    if x != -1:
        s, override_n2 = s, None
    else:
        s, override_n2 = s[:x], s[x + 1:]
        override_n2 = N2.from_str[override_n2.upper()]
    req = CountRequirement.from_str[s.upper()]
    yield req, override_n2


def make_count_req_table():
    text = """
                   DET_PRO  SHORTCUT
        INDEF      some     -
        DEF        all      -
        INTR       unk      all_one
        PROX       all      all_one
        DIST       all      all_one
        EXIST      one_of_n one_of_n
        ELECT_ANY  some     one_of_n
        ELECT_EVER unk      all_one
        UNIV_EVERY all/sing all/sing
        UNIV_ALL   all/plur all/sing
        NEG        none     none/sing
        ALT        one_of_n one_of_n
    """

    sss = map(lambda line: line.split(), text.strip().split('\n'))

    n = len(sss[0])
    for ss in sss[1:]:
        assert len(ss) == n + 1

    cors = []
    for ss in sss[1:]:
        s = ss[0]
        cor = SurfaceCorrelative.from_str[s]
        cors.append(cor)
    assert set(cors) == SurfaceCorrelative.values

    col_cor2req = {}
    for row_index in xrange(len(sss) - 1):
        for col_index in xrange(n):
            s = sss[row_index + 1][col_index + 1]
            for req in parse_count_req_entry(s):
                col = sss[0][col_index]
                cor = sss[row_index + 1][0]
                cor = SurfaceCorrelative.from_str[cor]
                col_cor2req[(col, cor)] = req
    return col_cor2req
