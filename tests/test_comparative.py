import yaml

from panoptes.ling.morph.comparative.comparative import ComparativeDegree, \
    ComparativeManager, ComparativePolarity
from panoptes.ling.morph.pronunciation.syllable_counter import SyllableCounter


def check(m, base, degree, want_derived):
    ss = want_derived.split()
    if len(ss) == 1:
        want_ss = None, ss[0]
    else:
        want_ss = ss
    got_ss = m.encode(degree, ComparativePolarity.POS, base)
    print
    print want_ss
    print got_ss


def main():
    syllable_counter = SyllableCounter.default()
    m = ComparativeManager.default(syllable_counter)

    fn = 'tests/comparative.yaml'
    jj = yaml.load(open(fn))

    for j in jj:
        print j['name']
        for base, er, est in j['triples']:
            check(m, base, ComparativeDegree.COMP, er)
            check(m, base, ComparativeDegree.SUPER, est)


if __name__ == '__main__':
    main()
