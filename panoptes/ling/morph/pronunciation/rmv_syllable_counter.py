import re
import yaml


def count_overlapping_distinct(regex, word):
    n = 0
    start_x = 0
    while True:
        m = regex.search(word, start_x)
        if m is None:
            return n
        n += 1
        start_x = 1 + m.start()
    return n


class RmvSyllableCounter(object):
    def __init__(self, subsyls, addsyls, exceptions_one):
        self.subsyls = subsyls
        self.addsyls = addsyls
        self.exceptions_one = exceptions_one

        self.vowel_re = re.compile('[^a-z]is')
        self.word_parts_re = re.compile('[^aeiouy]+')

    @staticmethod
    def from_file(fn):
        j = yaml.load(open(fn))

        subsyls = []
        for s in j['subsyls']:
            r = re.compile(s)
            subsyls.append(r)

        addsyls = []
        for s in j['addsyls']:
            r = re.compile(s)
            addsyls.append(r)

        exceptions_one = []
        for s in j['exceptions_one']:
            r = re.compile(s)
            exceptions_one.append(r)

        return RmvSyllableCounter(subsyls, addsyls, exceptions_one)

    @staticmethod
    def default():
        fn = 'panoptes/ling/morph/pronunciation/rmv_syllables.yaml'
        return RmvSyllableCounter.from_file(fn)

    def get_syllable_count(self, word):
        word = word.lower()

        # Split on clusters of vowels.
        word = self.vowel_re.sub('', word)
        word_parts = self.word_parts_re.split(word)
        word_parts = filter(bool, word_parts)
        n = len(word_parts)

        # Increment and decrement according to config data.
        for regex in self.subsyls:
            n -= count_overlapping_distinct(regex, word)
        for rgex in self.addsyls:
            n += count_overlapping_distinct(regex, word)

        # Exceptions.
        if word in self.exceptions_one:
            n -= 1

        # At least one.
        if not n:
            n = 1

        # TODO: figure out what is causing this bug.
        if 20 <= n:
            n = 3

        return n
