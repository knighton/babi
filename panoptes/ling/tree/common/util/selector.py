from panoptes.ling.glue.grammatical_number import N5, nx_le_nx_is_guaranteed


# "Melange" covers articles, interrogatives, demonstratives, and quantifiers, as
# in Zamenhoff's table of correlatives.
#
#   https://en.wikipedia.org/wiki/Pro-form
#
# On naming: it's kind of a mixture of different types of pro-forms.  I need
# "Selector" to refer to the object that contains count information as well as
# this enum.  Also,
#
#   https://en.wikipedia.org/wiki/Melange_(fictional_drug)
#
# Different types of elective and universal correlatives use different
# determiners/pronouns and may have different grammatical numbers (eg, "all cats
# are black" but "every cat is black"), so those entries are split.
Melange = enum("""Melange =
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


class Selector(object):
    """
    Internal field of common nouns.

    How common nouns handle grammatical number.

    Information is stored as:
    * a Quantifier (eg, all/some/one/unknown of them)
    * how many there are, as an N5 range (eg, singular/plural/two/many)
    * out of how many they were selected from, also an N5 range

    Examples:

    * "the black cat" -> DEF one out of one
    * "the black cats" -> DEF plural out of plural
    * "both black cats" -> UNIV_ALL dual out of dual
    * "any black cat" -> ELECT_ANY one out of plural
    * "no black cats" -> NEG zero of plural
    """

    def __init__(self, melange, n_min, n_max, of_n_min, of_n_max):
        self.melange = melange
        assert Melange.is_valid(self.melange)

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
            'melange': Melange.to_str[self.melange],
            'n_min': N5.to_str[self.n_min],
            'n_max': N5.to_str[self.n_max],
            'of_n_min': N5.to_str[self.n_min],
            'of_n_max': N5.to_str[self.n_min],
        }

    def is_definite(self):
        return self.melange == Melange.DEF

    def is_interrogative(self):
        return self.melange == Melange.INTR

    @staticmethod
    def load(d, loader):
        melange = Melange.from_str[d['melange']]
        n_min = N5.from_str[d['n_min']]
        n_max = N5.from_str[d['n_max']]
        of_n_min = N5.from_str[d['of_n_min']]
        of_n_max = N5.from_str[d['of_n_max']]
        return Selector(melange, n_min, n_max, of_n_min, of_n_max)
