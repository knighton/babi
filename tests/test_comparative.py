import yaml

from panoptes.ling.morph.comparative.comparative import ComparativeDegree, \
    ComparativeManager, ComparativePolarity
from panoptes.ling.morph.pronunciation.syllable_counter import SyllableCounter


def check(m, base, degree, want_derived):
    ss = want_derived.split()
    if len(ss) == 1:
        want_ss = None, ss[0]
    else:
        want_ss = tuple(ss)
    got_ss = m.encode(degree, ComparativePolarity.POS, base)
    try:
        assert want_ss == got_ss
    except:
        print 'encode() failed.'
        print 'want:', want_ss
        print 'got:', got_ss
        raise

    ok = False
    degs_pols_bases = m.decode(*want_ss)
    for deg, pol, got_base in degs_pols_bases:
        if deg == degree and pol == ComparativePolarity.POS and \
                got_base == base:
            ok = True
            break

    if not ok:
        print 'decode() failed.'
        print 'input:', want_derived
        print 'want:', ComparativeDegree.to_str[degree], \
                ComparativePolarity.to_str[ComparativePolarity.POS], base
        print 'got:'
        for deg, pol, got_base in degs_pols_bases:
            print '-', ComparativeDegree.to_str[deg], \
                    ComparativePolarity.to_str[pol], got_base
        assert False


def main():
    syllable_counter = SyllableCounter.default()
    m = ComparativeManager.default(syllable_counter)

    fn = 'tests/comparative.yaml'
    jj = yaml.load(open(fn))

    for j in jj:
        for base, er, est in j['triples']:
            check(m, base, ComparativeDegree.COMP, er)
            check(m, base, ComparativeDegree.SUPER, est)


if __name__ == '__main__':
    main()
