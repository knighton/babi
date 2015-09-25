from panoptes.ling.glue.grammatical_number import N5
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.glue.magic_token import PLACE_PREP
from panoptes.ling.tree.common.util.selector import Correlative, Selector
from panoptes.ling.tree.surface.util.pro_adverb import ProAdverbManager


def main():
    m = ProAdverbManager()

    proximal_sing = Selector(
        Correlative.PROX, N5.SING, N5.SING, N5.SING, N5.SING)
    r = m.say(PLACE_PREP, proximal_sing, 'place', False)
    assert r.tokens == ['here']
    assert r.conjugation == Conjugation.S3
    assert r.eat_prep == True

    ss = 'here',
    aaa = m.parse(ss)
    assert len(aaa) == 1
    prep, selector, noun = aaa[0]
    assert prep == PLACE_PREP
    assert selector.dump() == proximal_sing.dump()
    assert noun == 'place'


if __name__ == '__main__':
    main()
