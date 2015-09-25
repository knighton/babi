from copy import deepcopy

from panoptes.etc.enum import enum
from panoptes.ling.glue.grammatical_number import compints_from_nx, N2, N5, \
    nx_to_nxs


# "Correlative" covers articles, interrogatives, demonstratives, and
# quantifiers, as in Zamenhoff's table of correlatives.
#
#   https://en.wikipedia.org/wiki/Pro-form
#
# Different types of elective and universal correlatives use different
# determiners/pronouns and may have different grammatical numbers (eg, "all cats
# are black" but "every cat is black"), so those entries are split.
Correlative = enum("""Correlative =
    INDEF
    DEF

    INTR

    PROX
    DIST

    EXIST
    ELECT_ANY
    ELECT_EVER
    UNIV_EVERY
    UNIV_ALL
    NEG
    ALT
""")


CountRestriction = enum("""CountRestriction =
    NONE ANY ONE_OF_PLURAL SOME ALL_ONE ALL""")


# CountRestriction -> implementation that compares compints.
COUNT_RESTRICTION2CHECK = {
    # Negative.
    CountRestriction.NONE: lambda a, b: 0 == a <= b,

    # Unknown (any).
    CountRestriction.ANY: lambda a, b: 0 <= a <= b,

    # Indefinite forms: less than all of them.
    CountRestriction.ONE_OF_PLURAL: lambda a, b: 1 == a < b,
    CountRestriction.SOME: lambda a, b: 1 <= a < b,

    # Definite forms: all of them.
    CountRestriction.ALL_ONE: lambda a, b: 1 == a == b,
    CountRestriction.ALL: lambda a, b: 1 <= a == b,
}


class Selector(object):
    """
    Internal field of common nouns.

    How common nouns handle grammatical number.

    Information is stored as:
    * a Correlative (eg, all/some/one/unknown of them)
    * how many there are, as an N5 range (eg, singular/plural/two/many)
    * out of how many they were selected from, also an N5 range

    Examples:

    * "the black cat" -> DEF one out of one
    * "the black cats" -> DEF plural out of plural
    * "both black cats" -> UNIV_ALL dual out of dual
    * "any black cat" -> ELECT_ANY one out of plural
    * "no black cats" -> NEG zero of plural
    """

    def __init__(self, correlative, n_min, n_max, of_n_min, of_n_max):
        self.correlative = correlative
        assert Correlative.is_valid(self.correlative)

        self.n_min = n_min
        self.n_max = n_max
        assert N5.is_valid(self.n_min)
        assert N5.is_valid(self.n_max)
        assert self.n_min <= self.n_max

        self.of_n_min = of_n_min
        self.of_n_max = of_n_max
        assert N5.is_valid(self.of_n_min)
        assert N5.is_valid(self.of_n_max)
        assert self.of_n_min <= self.of_n_max

    def dump(self):
        return {
            'type': 'Selector',
            'correlative': Correlative.to_str[self.correlative],
            'n_min': N5.to_str[self.n_min],
            'n_max': N5.to_str[self.n_max],
            'of_n_min': N5.to_str[self.of_n_min],
            'of_n_max': N5.to_str[self.of_n_max],
        }

    def is_indefinite(self):
        return self.correlative == Correlative.INDEF

    def is_definite(self):
        return self.correlative == Correlative.DEF

    def is_interrogative(self):
        return self.correlative == Correlative.INTR

    def guess_n(self, NX):
        return nx_to_nxs(self.n_max, NX)[-1]

    def guess_of_n(self, NX):
        return nx_to_nxs(self.of_n_max, NX)[-1]

    def to_compints(self):
        aa = []
        for n in xrange(self.n_min, self.n_max + 1):
            aa += compints_from_nx(n)
        aa = set(aa)

        bb = []
        for n in xrange(self.of_n_min, self.of_n_max + 1):
            bb += compints_from_nx(n)
        bb = set(bb)

        return aa, bb

    def decide_grammatical_number(self, cor2res_gno):
        """
        (Correlative -> (CountRestriction or None, N2 or None)) -> N2 or None

        Get whether to say the owning common noun as singular or plural, taking
        exceptions into account.

        Returns None if we are not valid (requires the input table to
        fully determine).
        """
        count_restriction, gram_num_override = cor2res_gno[self.correlative]

        # If there is no CountRestriction, it's not possible (eg, DEF is okay
        # for correlatives ("the"), but there is no such pro-adverb).
        if not count_restriction:
            return None

        # Make sure that the "how many" range, the "out of" range, and the
        # count restriction jive.
        aa, bb = self.to_compints()
        f = COUNT_RESTRICTION2CHECK[count_restriction]
        possible = False
        for a in aa:
            for b in bb:
                if f(a, b):
                    possible = True
        if not possible:
            return None

        # Determine the correct N2.
        if gram_num_override:
            n2 = gram_num_override
        else:
            if self.n_min == N5.SING:
                n2 = N2.SING
            else:
                n2 = N2.PLUR

        return n2

    def restricted_to_grammatical_number(self, required_gram_n2, cor2res_gno):
        """
        required gram number, (cor -> (res, gno)) -> list of Selector

        Restrict my count ranges to only fit the given grammatical number.
        Returns new objects.
        """
        count_restriction, gram_num_override = cor2res_gno[self.correlative]

        # If it is not even possible, return None.
        if not count_restriction:
            return []

        # If we are forced to pick a grammatical number, we are either fine or
        # hosed.
        if gram_num_override:
            if gram_num_override == required_gram_num:
                return [deepcopy(self)]
            else:
                return []

        # Else, collect the grammatical numbers as N2s.
        gram_nums = set()
        for n2 in xrange(self.n_min, self.n_max + 1):
            gram_nums.add(n2)

        # If there's just one, we are either fine or hosed.
        if len(gram_nums) == 1:
            got = list(gram_nums)[0]
            if got == required_gram_num:
                return [deepcopy(self)]
            else:
                return []

        # If not one, there must be two since the ranges are inclusive (there
        # can't be zero and there are only two possible values).
        assert len(gram_nums) == 2

        # Which part do we have to filter out?
        rr = []
        if required_gram_num == N2.SING:
            # If it must be singular, return a Selector with the count range set
            # to N5.SING, if that is in our range -- else we're hosed.
            if self.n_min <= N5.SING <= self.n_max:
                r = Selector(self.correlative, N5.SING, N5.SING, self.of_n_min,
                             self.of_n_max)
                rr.append(r)
            else:
                return []
        else:
            # If it must be plural, split the range on both sides of N5.SING
            # (zero and > 1).
            if self.n_min == N5.ZERO:
                r = Selector(self.correlative, N5.ZERO, N5.ZERO, self.of_n_min,
                             self.of_n_max)
                rr.appenr(r)

            if N5.DUAL <= self.n_max:
                r = Selector(self.correlative, N5.DUAL, self.n_max,
                             self.of_n_min, self.of_n_max)
                rr.append(r)

        # Now, reapply the count restriction to the smaller ranges in order to
        # drop of_n's that don't fit anymore (eg, if the word is "the" and the
        # required grammatical count is singular, it will make the of_n range
        # N5.SING to match the n range).
        count_restriction = cor2res_gno[self.correlative][0]
        return map(lambda sel: \
            sel.fitted_to_count_restriction(count_restriction), rr)

    def fitted_to_count_restriction(self, count_restriction):
        """
        CountRestriction -> Selector or None

        Attempt to shrink our ranges to fit the count restriction.  Returns a
        new Selector or None if it ruled out everything.
        """
        check = COUNT_RESTRICTION2CHECK[count_restriction]

        possible_ns_ofs = []
        for n5 in xrange(self.n_min, self.n_max + 1):
            aa = compints_from_nx(n5)
            for of_n5 in xrange(self.of_n_min, self.of_n_max + 1):
                bb = compints_from_nx(of_n5)
                possible = False
                for a in aa:
                    for b in bb:
                        if check(a, b):
                            possible = True
                            break
                if possible:
                    possible_ns_ofs.append((n5, of_n5))

        if not possible_ns_ofs:
            return None

        ns, ofs = map(sorted, map(set, zip(*possible_ns_ofs)))

        assert ns == range(ns[0], ns[-1] + 1)

        n_min = ns[0]
        n_max = ns[-1]

        assert ofs == range(ofs[0], ofs[-1] + 1)

        of_n_min = ofs[0]
        of_n_max = ofs[-1]

        return Selector(self.correlative, n_min, n_max, of_n_min, of_n_max)

    @staticmethod
    def load(d):
        correlative = Correlative.from_str[d['correlative']]
        n_min = N5.from_str[d['n_min']]
        n_max = N5.from_str[d['n_max']]
        of_n_min = N5.from_str[d['of_n_min']]
        of_n_max = N5.from_str[d['of_n_max']]
        return Selector(correlative, n_min, n_max, of_n_min, of_n_max)

    @staticmethod
    def from_correlative(correlative, count_restriction):
        sel = Selector(correlative, N5.ZERO, N5.MANY, N5.ZERO, N5.MANY)
        return sel.fitted_to_count_restriction(count_restriction)
