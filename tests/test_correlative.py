from panoptes.ling.glue.correlative import SurfaceCorrelative
from panoptes.ling.glue.grammatical_number import N3, N5
from panoptes.ling.tree.surface.util.correlative import CorrelativeManager
from panoptes.ling.tree.surface.util.count_restriction import \
    CountRestrictionChecker


def main():
    counts = CountRestrictionChecker()
    m = CorrelativeManager(counts)

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


if __name__ == '__main__':
    main()
