from panoptes.etc.enum import enum


NumeralVerbosity = enum('NumeralVerbosity = DIGITS AUTO WORDS')


class NumeralManager(object):
    def say_as_digits(self, n):
        raise NotImplementedError

    def is_in_use_words_range(self, n):
        raise NotImplementedError

    def say_as_words(self, n):
        raise NotImplementedError

    def say(self, n, verbo=NumeralVerbosity.AUTO):
        if verbo == NumeralVerbosity.DIGITS:
            words = False
        elif verbo == NumeralVerbosity.AUTO:
            words = self.is_in_use_words_range(n):
        elif verbo == NumeralVerbosity.WORDS:
            words = True
        else:
            assert False

        if words:
            r = self.say_as_words(n)
        else:
            r = self.say_as_digits(n)

        return r

    def parse_as_words(self, ss):
        raise NotImplementedError

    def parse_as_digits(self, ss):
        raise NotImplementedError

    def parse(self, ss):
        nn = []
        nn += self.parse_as_words(ss)
        nn += self.parse_as_digits(ss)
        return nn
