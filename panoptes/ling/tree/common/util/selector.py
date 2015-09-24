from panoptes.ling.glue.grammatical_number import compints_from_nx, N2, N5, \
    nx_le_nx_is_guaranteed, nx_to_nxs


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


# CountRestriction -> inclusive N5 ranges for (how many, out of).
COUNT_RESTRICTION2WORST_BOUNDS = {
    CountRestriction.NONE:          (N5.ZERO, N5.ZERO, N5.ZERO, N5.MANY),

    CountRestriction.ANY:           (N5.ZERO, N5.MANY, N5.ZERO, N5.MANY),

    CountRestriction.ONE_OF_PLURAL: (N5.SING, N5.SING, N5.DUAL, N5.MANY),
    CountRestriction.SOME:          (N5.SING, N5.MANY, N5.SING, N5.MANY),

    CountRestriction.ALL_ONE:       (N5.SING, N5.SING, N5.SING, N5.SING),
    CountRestriction.ALL:           (N5.SING, N5.MANY, N5.SING, N5.MANY),
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
        assert nx_le_nx_is_guaranteed(self.n_min, self.n_max)

        self.of_n_min = of_n_min
        self.of_n_max = of_n_max
        assert N5.is_valid(self.of_n_min)
        assert N5.is_valid(self.of_n_max)
        assert nx_le_nx_is_guaranteed(self.of_n_min, self.of_n_max)

    def dump(self):
        return {
            'type': 'Selector',
            'correlative': Correlative.to_str[self.correlative],
            'n_min': N5.to_str[self.n_min],
            'n_max': N5.to_str[self.n_max],
            'of_n_min': N5.to_str[self.n_min],
            'of_n_max': N5.to_str[self.n_min],
        }

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
        # for correlatives ("the"), but there is no such shortcut).
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

    def shrink(self, count_restriction):
        aa = COUNT_RESTRICTION2WORST_BOUNDS[count_restriction]
        self.n_min = max(self.n_min, aa[0])
        self.n_max = min(self.n_max, aa[1])
        self.of_n_min = max(self.of_n_min, aa[2])
        self.of_n_max = min(self.of_n_max, aa[3])

    @staticmethod
    def load(d, loader):
        correlative = Correlative.from_str[d['correlative']]
        n_min = N5.from_str[d['n_min']]
        n_max = N5.from_str[d['n_max']]
        of_n_min = N5.from_str[d['of_n_min']]
        of_n_max = N5.from_str[d['of_n_max']]
        return Selector(correlative, n_min, n_max, of_n_min, of_n_max)

    @staticmethod
    def from_correlative(correlative, count_restriction):
        n_min, n_max, of_n_min, of_n_max = \
            COUNT_RESTRICTION2WORST_BOUNDS[count_restriction]
        return Selector(correlative, n_min, n_max, of_n_min, of_n_max)
