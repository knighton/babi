from panoptes.ling.glue.grammatical_number import N5, nx_le_nx_is_guaranteed


# Selectors allow determiners, articles, quantifiers, and the like.
#
# Different types of elective and universal correlatives use different
# determiners/pronouns and may have different grammatical numbers (eg, "all cats
# are black" but "every cat is black").
Selector = enum("""Selector =
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


class CommonNounGrammaticalNumber(object):
    """
    How common nouns handle grammatical number.

    Information is stored as:
    * a selector (eg, all/some/one/unknown of them)
    * how many there are, as an N5 range (eg, singular/plural/two/many)
    * out of how many they were selected from, also an N5 range

    Examples:

    * "the black cat" -> DEF one out of one
    * "both black cats" -> UNIV_ALL dual out of dual
    * "any black cat" -> ELECT_ANY one out of plural
    * "no black cats" -> NEG zero of plural
    """

    def __init__(self, selector, n_min, n_max, of_n_min, of_n_max):
        self.selector = selector
        assert Selector.is_valid(self.selector)

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
            'type': 'CommonNounGrammaticalNumber',
            'selector': Selector.to_str[self.selector],
            'n_min': N5.to_str[self.n_min],
            'n_max': N5.to_str[self.n_max],
            'of_n_min': N5.to_str[self.n_min],
            'of_n_max': N5.to_str[self.n_min],
        }

    @staticmethod
    def load(d, loader):
        selector = Selector.from_str[d['selector']]
        n_min = N5.from_str[d['n_min']]
        n_max = N5.from_str[d['n_max']]
        of_n_min = N5.from_str[d['of_n_min']]
        of_n_max = N5.from_str[d['of_n_max']]
        return CommonNounGrammaticalNumber(
            selector, n_min, n_max, of_n_min, of_n_max)
