from panoptes.ling.glue.grammatical_number import N5
from panoptes.ling.tree.common.util.selector import Correlative, Selector
from panoptes.ling.tree.surface.util.pronoun import DetPronounManager


def check(det_pronoun_mgr, s, expect_selectors):
    ss = s.split()
    if len(ss) == 1:
        s = ss[0]
        f = det_pronoun_mgr.parse_pro
    elif len(ss) == 2:
        s = ss[0]
        assert ss[-1] == '_'
        f = det_pronoun_mgr.parse_det
    got_selectors = f(s)
    got = map(lambda sel: sel.dump(), got_selectors)
    expected = map(lambda sel: sel.dump(), expect_selectors)

    try:
        assert got == expected
    except:
        import json
        print
        print 'ERROR'
        print
        print 'Expected:'

        for d in expected:
            print json.dumps(d, indent=4, sort_keys=True)

        print
        print 'Got:'

        for d in got:
            print json.dumps(d, indent=4, sort_keys=True)

        raise


def main():
    m = DetPronounManager()

    check(m, 'the', [])

    check(m, 'the _', [
        Selector(Correlative.DEF, N5.SING, N5.MANY, N5.SING, N5.MANY),
    ])

    """
    r = m.say(SurfaceCorrelative.DEF, N3.SING, N5.SING, False)
    assert r.tokens == ['the']

    r = m.say(SurfaceCorrelative.DEF, N3.SING, N5.SING, True)
    assert not r

    r = m.say(SurfaceCorrelative.DEF, N3.PLUR, N5.SING, False)
    assert not r

    assert set(m.parse_det('both')) == set([
        (SurfaceCorrelative.UNIV_ALL, N3.PLUR, N5.DUAL),
    ])

    assert set(m.parse_pro('both')) == set([
        (SurfaceCorrelative.UNIV_ALL, N3.PLUR, N5.DUAL),
    ])

    assert set(m.parse_det('any')) == set([
        (SurfaceCorrelative.ELECT_ANY, N3.SING, N5.FEW),
        (SurfaceCorrelative.ELECT_ANY, N3.PLUR, N5.FEW),
        (SurfaceCorrelative.ELECT_ANY, N3.SING, N5.MANY),
        (SurfaceCorrelative.ELECT_ANY, N3.PLUR, N5.MANY),
    ])

    assert set(m.parse_pro('the')) == set([])

    assert set(m.parse_det('the')) == set([
        (SurfaceCorrelative.DEF, N3.SING, N5.SING),
        (SurfaceCorrelative.DEF, N3.PLUR, N5.DUAL),
        (SurfaceCorrelative.DEF, N3.PLUR, N5.FEW),
        (SurfaceCorrelative.DEF, N3.PLUR, N5.MANY),
    ])

    assert set(m.parse_pro('neither')) == set([
        (SurfaceCorrelative.NEG, N3.ZERO, N5.DUAL),
    ])
    """


if __name__ == '__main__':
    main()
