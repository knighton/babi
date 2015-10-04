import math

from panoptes.ling.morph.numeral.base import NumeralManager


def list_find(aa, to_find):
    for i, a in enumerate(aa):
        if a == to_find:
            return i
    return -1


class CardinalManager(NumeralManager):
    def __init__(self):
        self.neg_names = ['minus', 'negative']

        self.one_names = """zero one two three four five six seven eight nine
            ten eleven twelve thirteen fourteen fifteen sixteen seventeen
            eighteen nineteen""".split()
        self.one_name2n = dict(zip(self.one_names, range(len(self.one_names))))

        self.ten_names = [None, None] + """twenty thirty fourty fifty sixty
            seventy eighty ninety""".split()
        self.ten_name2n = dict(zip(self.ten_names, range(len(self.ten_names))))

        self.thou_pow_names = [None, 'thousand']
        for prefix in 'm b tr quadr quint sext sept oct non dec'.split():
            s = prefix + 'illion'
            self.thou_pow_names.append(s)
        self.thou_pow_name2n = dict(zip(
            self.thou_pow_names, range(len(self.thou_pow_names))))

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

    def parse_as_words_under_100(self, ss):
        rr = []
        z = len(ss)
        if z == 1:
            s, = ss

            n = self.one_name2n.get(s)
            if n is not None:
                rr.append(n)

            n = self.ten_name2n.get(s)
            if n is not None:
                rr.append(n * 10)
        elif z == 2:
            ten, one = ss
            ten_n = self.ten_name2n.get(ten)
            if ten_n is None:
                return []

            one_n = self.one_name2n.get(one)
            if one_n is None:
                return []

            n = ten_n * 10 + one_n
            rr.append(n)
        else:
            pass
        return rr

    def parse_as_words_under_1000(self, ss):
        # Hundreds.
        x = list_find(ss, 'hundred')
        if x == -1:
            hundreds_nn = [0]
        else:
            ss_hundreds = ss[:x]
            hundreds_nn = self.parse_as_words_under_100(ss_hundreds)
            hundreds_nn = map(lambda n: n * 100, hundreds_nn)

        # Tens and ones.
        ss_ones = ss[x + 1:]
        if not ss_ones:
            if ss:
                return hundreds_nn
            else:
                return []  # Must have something.

        ones_nn = self.parse_as_words_under_100(ss_ones)
        rr = []
        for hundred in hundreds_nn:
            for one in ones_nn:
                rr.append(hundred + one)
        return rr

    def parse_as_words(self, ss):
        if not ss:
            return []

        first = ss[0]
        if first in self.neg_names:
            is_neg = True
            ss = ss[1:]
        else:
            is_neg = False

        # Find groupings within the words.
        xx = []
        for i, s in enumerate(ss):
            if s in self.thou_pow_names:
                xx.append(i)

        rr = [0]

        # Parse each grouping.
        for i, x in enumerate(xx):
            if i == 0:
                begin = 0
            else:
                begin = xx[i - 1] + 1
            sub_ss = ss[begin : x]
            sub_nn = self.parse_as_words_under_1000(sub_ss)
            thou_pow = self.thou_pow_name2n[ss[x]]
            sub_nn = map(lambda n: n * (1000 ** thou_pow), sub_nn)
            if not sub_nn:
                return []
            new_rr = []
            for r in rr:
                for n in sub_nn:
                    new_rr.append(r + n)
            rr = new_rr

        # Get the last one, if there is one.
        if xx:
            sub_ss = ss[xx[-1] + 1:]
        else:
            sub_ss = ss
        if sub_ss:
            sub_nn = self.parse_as_words_under_1000(sub_ss)
            if not sub_nn:
                return []
            new_rr = []
            for r in rr:
                for n in sub_nn:
                    new_rr.append(r + n)
            rr = new_rr

        if is_neg:
            rr = map(lambda n: n * -1, rr)

        return rr

    def parse_as_digits(self, ss):
        if len(ss) != 1:
            return []

        s, = ss
        try:
            n = int(s)
            return [n]
        except:
            return []
