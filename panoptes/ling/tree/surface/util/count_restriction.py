from panoptes.etc.enum import enum
from panoptes.ling.glue.grammatical_number import N2, compints_from_nx, nx_to_nx


CountRestriction = enum("""CountRestriction =
    NONE ANY ONE_OF_PLURAL SOME ALL_ONE ALL""")


class CountRestrictionChecker(object):
    def __init__(self):
        self.cr2f = {
            # Zero.
            CountRestriction.NONE: lambda a, b: 0 == a <= b,

            # Unknown (any).
            CountRestriction.ANY: lambda a, b: 0 <= a <= b,

            # Indefinite: less than all of them.
            CountRestriction.ONE_OF_PLURAL: lambda a, b: 1 == a < b,
            CountRestriction.SOME: lambda a, b: 1 <= a < b,

            # Definite: all of them.
            CountRestriction.ALL_ONE: lambda a, b: 1 == a == b,
            CountRestriction.ALL: lambda a, b: 1 <= a == b,
        }

    def is_possible(self, count_restriction, n, of_n):
        aa = compints_from_nx(n)
        bb = compints_from_nx(of_n)
        for a in aa:
            for b in bb:
                if self.cr2f[count_restriction](a, b):
                    return True
        return False

    def get_grammatical_number(self, n, of_n, override_gram_number):
        """
        args -> N2
        """
        if override_gram_num:
            return override_gram_num
        else:
            return nx_to_nx(n, N2)
