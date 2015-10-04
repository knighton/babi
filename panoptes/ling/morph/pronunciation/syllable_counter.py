from panoptes.ling.morph.pronunciation.cmudict import CmuDict
from panoptes.ling.morph.pronunciation.rmv_syllable_counter import RmvSyllableCounter


class SyllableCounter(object):
    def __init__(self, cmu, rmv):
        self.cmu = cmu
        self.rmv = rmv
        self.cache = {}

    @staticmethod
    def default():
        cmu = CmuDict.default()
        rmv = RmvSyllableCounter.default()
        return SyllableCounter(cmu, rmv)

    def get_syllable_count(self, word):
        n = self.cache.get(word)
        if n:
            return n

        nn = self.cmu.get_syllable_counts(word)
        if nn:
            n, = nn
            self.cache[word] = n
            return n

        n = self.rmv.get_syllable_count(word)
        self.cache[word] = n
        return n
