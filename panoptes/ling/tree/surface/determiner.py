from collections import defaultdict

from ling.glue.correlative import SurfaceCorrelative
from ling.glue.grammatical_number import N5


def parse_entry(s):
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
    for is_pro, is_plur, s in zip(is_pros, is_plurs, ss):
        if s == '-':
            continue
        yield is_pro, is_plur, s


def make_det_pro_table():
    text = """
                   SING  DUAL      FEW               MANY
        INDEF      -     <a>/one   <a>:some/one:some <a>:some/one:some
        DEF        the/- the/-     the/-             the/-
        INTR       -     which     which             what
        PROX       this  these     these             these
        DIST       that  those     those             those
        EXIST      -     one       some/one:some     some/one:some
        ELECT_ANY  -     either    any               any
        ELECT_EVER -     whichever whichever         whatever
        UNIV_EVERY -     -         every/-           every/-
        UNIV_ALL   -     both      all               all
        NEG        -     neither   no/none           no/none
        ALT        -     -         another           another
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
            for is_pro, is_plur, s in parse_entry(s):
                cor_pro_plur_of2ss[(cor, is_pro, is_plur, of)].append(s)
    return cor_pro_plur_of2ss
