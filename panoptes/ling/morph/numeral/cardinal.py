import math

from panoptes.ling.morph.numeral.base import NumeralManager


class CardinalManager(object):
    def __init__(self):
        self.one_names = """zero one two three four five six seven eight nine
            ten eleven twelve thirteen fourteen fifteen sixteen seventeen
            eighteen nineteen""".split()

        self.ten_names = [None, None] + """twenty thirty fourty fifty sixty
            seventy eighty ninety""".split()

        self.thou_pow_names = ['', 'thousand']
        for prefix in 'm b tr quadr quint sext sept oct non dec'.split():
            s = prefix + 'illion'
            self.thou_pow_names.append(s)

        self.use_words_range = (0, 9)

    def say_as_digits(self, n):
        return [str(n)]

    def is_in_use_words_range(self, n):
        return self.use_words_range[0] <= n <= self.use_words_range[1]

    def say_as_words_under_1000(self, n):
        rr = []

        if 100 <= n:
            s = self.one_names[n / 100]
            rr.append(s)
            rr.append('hundred')
            n %= 100

        if 20 <= n:
            s = self.ten_names[n / 10]
            rr.append(s)
            n %= 10

        if n:
            s = self.one_names[n]
            rr.append(s)

        return rr

    def say_as_words(self, n):
        if n == 0:
            s = self.one_names[n]
            return [s]

        rr = []
        if n < 0:
            n = abs(n)
            rr.append('negative')

        max_thou_pow = int(math.log(n, 1000))
        for thou_pow in reversed(range(max_thou_pow + 1)):
            div = 1000 ** thou_pow
            under_1000 = int(n / div)
            if under_1000:
                rr += self.say_as_words_under_1000(under_1000)
                name = self.thou_pow_names[thou_pow]
                if name:
                    rr.append(name)
            n %= div

        return rr

    def parse_as_words(self, ss):
        raise NotImplementedError

    def parse_as_digits(self, ss):
        if len(ss) != 1:
            return []

        s, = ss
        n = int(s)
        return [n]
