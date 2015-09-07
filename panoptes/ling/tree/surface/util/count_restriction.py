from etc.enum import enum
from ling.glue.grammatical_number import N2, nx_to_nx, NX2COMP_INTS


CountRestriction = enum("""CountRestriction =
    NONE ANY ONE_OF_PLURAL SOME ALL_ONE ALL""")


class CountRestrictionChecker(object):
    def __init__(self):
        self.enum2f = {
            # Zero.
            CountRestriction.NONE: 0 == a <= b,

            # Unknown (any).
            CountRestriction.ANY: 0 <= a <= b,

            # Indefinite: less than all of them.
            CountRestriction.ONE_OF_PLURAL: 1 == a < b,
            CountRestirction.SOME: 1 <= a < b,

            # Definite: all of them.
            CountRestriction.ALL_ONE: 1 == a == b,
            CountRestriction.ALL: 1 <= a == b,
        }

    def is_possible(self, count_restriction, n, of_n):
        aa = NX2COMP_INTS[n]
        bb = NX2COMP_INTS[of_n]
        for a in aa:
            for b in bb:
                if self.enum2f[count_restriction](a, b):
                    return True
        assert False

    def get_grammatical_number(self, n, of_n, override_gram_number):
        """
        args -> N2
        """
        if override_gram_num:
            return override_gram_num
        else:
            return nx_to_nx(n, N2)
