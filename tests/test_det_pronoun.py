from panoptes.ling.glue.grammatical_number import N2, N5
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.common.util.selector import Correlative, Selector
from panoptes.ling.tree.surface.util.pronoun import DetPronounManager
from panoptes.ling.tree.surface.base import SayResult


def say(det_pronoun_mgr, selector, is_pro, expect_r):
    if is_pro:
        f = det_pronoun_mgr.say_pronoun
    else:
        f = det_pronoun_mgr.say_determiner
    r = f(selector)
    if r == None:
        assert r == expect_r
    else:
        assert r.dump() == expect_r.dump()


def test_say(m):
    selector = Selector(Correlative.DEF, N5.FEW, N5.FEW, N5.FEW, N5.FEW)
    r = SayResult(tokens=['the'], conjugation=Conjugation.P3, eat_prep=False)
    say(m, selector, False, r)

    selector = Selector(Correlative.DEF, N5.SING, N5.SING, N5.SING, N5.SING)
    r = SayResult(tokens=['the'], conjugation=Conjugation.S3, eat_prep=False)
    say(m, selector, False, r)

    selector = Selector(Correlative.DEF, N5.SING, N5.SING, N5.SING, N5.SING)
    r = None
    say(m, selector, True, r)

    selector = Selector(Correlative.NEG, N5.ZERO, N5.ZERO, N5.DUAL, N5.DUAL)
    r = SayResult(tokens=['neither'], conjugation=Conjugation.P3,
                  eat_prep=False)
    say(m, selector, False, r)

    selector = Selector(Correlative.NEG, N5.ZERO, N5.ZERO, N5.DUAL, N5.DUAL)
    r = SayResult(tokens=['neither'], conjugation=Conjugation.P3,
                  eat_prep=False)
    say(m, selector, True, r)

    selector = Selector(Correlative.NEG, N5.ZERO, N5.ZERO, N5.FEW, N5.MANY)
    r = SayResult(tokens=['no'], conjugation=Conjugation.P3,
                  eat_prep=False)
    say(m, selector, False, r)

    selector = Selector(Correlative.NEG, N5.ZERO, N5.ZERO, N5.FEW, N5.MANY)
    r = SayResult(tokens=['none'], conjugation=Conjugation.P3,
                  eat_prep=False)
    say(m, selector, True, r)


def parse(det_pronoun_mgr, s, expect_selectors):
    ss = s.split()
    if len(ss) == 1:
        s = ss[0]
        f = det_pronoun_mgr.parse_pronoun
    elif len(ss) == 2:
        s = ss[0]
        assert ss[-1] == '_'
        f = det_pronoun_mgr.parse_determiner
    got_selectors = f(s)
    got = map(lambda sel: sel.dump(), got_selectors)
    expected = map(lambda sel: sel.dump(), expect_selectors)

    try:
        assert got == expected
    except:
        import json
        print
        print 'ERROR:', s
        print
        print 'Expected:'

        for d in expected:
            print json.dumps(d, indent=4, sort_keys=True)

        print
        print 'Got:'

        for d in got:
            print json.dumps(d, indent=4, sort_keys=True)

        raise


def test_parse(m):
    parse(m, 'the', [])

    parse(m, 'the _', [
        Selector(Correlative.DEF, N5.SING, N5.MANY, N5.SING, N5.MANY),
    ])

    parse(m, 'this', [
        Selector(Correlative.PROX, N5.SING, N5.SING, N5.SING, N5.SING),
    ])

    parse(m, 'both', [
        Selector(Correlative.UNIV_ALL, N5.DUAL, N5.DUAL, N5.DUAL, N5.DUAL),
    ])

    parse(m, 'neither', [
        Selector(Correlative.NEG, N5.ZERO, N5.ZERO, N5.DUAL, N5.DUAL),
    ])

    parse(m, 'either', [
        Selector(Correlative.ELECT_ANY, N5.SING, N5.SING, N5.DUAL, N5.DUAL),
    ])

    parse(m, 'any', [
        Selector(Correlative.ELECT_ANY, N5.SING, N5.MANY, N5.FEW, N5.MANY),
    ])


def main():
    m = DetPronounManager()

    test_say(m)

    test_parse(m)


if __name__ == '__main__':
    main()
