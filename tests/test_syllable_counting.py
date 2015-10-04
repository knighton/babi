from collections import defaultdict

from panoptes.ling.morph.pronunciation.cmudict import CmuDict
from panoptes.ling.morph.pronunciation.rmv_syllable_counter import RmvSyllableCounter


def main():
    cmu = CmuDict.default()
    rmv = RmvSyllableCounter.default()
    off2count = defaultdict(int)
    for word in cmu.word2pronuns:
        true_nn = cmu.get_syllable_counts(word)
        guess_n = rmv.get_syllable_count(word)

        min_off = None
        for true_n in true_nn:
            off = guess_n - true_n
            if min_off is None or abs(off) < abs(min_off):
                min_off = off

        off2count[min_off] += 1
    a = min(off2count)
    z = max(off2count)
    for i in range(a, z + 1):
        print '%d\t%d' % (i, off2count[i])


if __name__ == '__main__':
    main()
