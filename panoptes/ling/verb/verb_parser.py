from collections import defaultdict

from lang.verb.conjugation import Conjugator


def remove_lemma_specific_word(sss):
    if sss[1]:
        return tuple(sss[0]), tuple(sss[1][:-1])
    else:
        return None


def deverb(sss):
    return tuple(sss[0]), tuple(sss[1][:-1])


def save_lookup_tables(be, pro, main, f):
    """
    be, pro, main, f -> None
    """
    assert False  # XXX


def load_lookup_tables(f):
    """
    f -> be, pro, main
    """
    assert False  # XXX


def construct_lookup_tables():
    """
    None -> be, pro, main
    """
    assert False  # XXX


class VerbParser(object):
    def __init__(self, conjugator, be_sss2vv, pro_verb_sss2vv, main_sss2vv):
        self.conjugator = conjugator
        assert isinstance(self.conjugator, Conjugator)

        # (pre words, main words) -> list of SurfaceVerb.
        #
        # The "to be" table.  "To be" conjugates specially.
        self.to_be_sss2vv = to_be_sss2vv
        assert isinstance(self.to_be_sss2vv, defaultdict)

        # (pre words, main words) -> list of SurfaceVerb.
        #
        # Pro-verbs also conjugate specially.
        self.pro_verb_sss2vv = pro_verb_sss2vv
        assert isinstance(self.pro_verb_sss2vv, defaultdict)

        # (pre words, main words with int) -> list of de-lemma'd SurfaceVerb.
        #
        # Table for everything else.  Replace conjugated lemma-specific word
        # with its field index to use.
        self.main_sss2vv = main_sss2vv
        assert isinstance(self.main_sss2vv, defaultdict)

        # Used by main_sss2vv parsing.
        self.deverbed_sss_set = \
            set(filter(bool, map(remove_lemma_specific_word, self.main_sss2vv)))

    @staticmethod
    def load(conjugator, f):
        be, pro, main = load_lookup_tables(f)
        return VerbParser(conjugator, be, pro, main)

    @staticmethod
    def construct(conjugator, f):
        be, pro, main = construct_lookup_tables()
        save_lookup_tables(be, pro, main, f)
        return VerbParser(conjugator, be, pro, main)

    @staticmethod
    def load_or_construct(conjugator, f):
        try:
            return VerbParser.load(conjugator, f)
        except:
            return VerbParser.construct(conjugator, f)

    def parse_field_index_replacing(self, sss):
        """
        (pre words tuple, main words tuple) -> list of SurfaceVerb
        """
        # It must have main words on the right.
        if not sss[1]:
            return []

        # Lemma-specific conjugated word must be verified to look like a verb,
        # as it isn't implicity checked by the lookup table generation like the
        # others.
        last = sss[1][-1]
        if not last.islower():
            return []

        # The lemma-agnostic remainder of the verb words must be known.
        deverbed_sss = deverb(sss)
        if deverbed_sss not in self.deverbed_sss_set:
            return []

        # Decode what the lemma-specific word means.
        rr = []
        for lemma, field_index in self.conjugator.identify_word(last):
            # Look up the field index-replaced form in the table.
            key = (deverbed_sss[0], tuple(deverbed_sss[1] + [str(field_index)]))
            sub_rr = self.main_sss2vv[key]

            # Put our lemma into the results found.
            for r in sub_rr:
                r.intrinsics.lemma = lemma

            rr += sub_rr
        return rr

    def parse(self, sss):
        """
        (pre words tuple, main words tuple) -> list of SurfaceVerb
        """
        rr = []
        rr += self.to_be_sss2vv[sss]
        rr += self.pro_verb_sss2vv[sss]
        rr += self.parse_field_index_replacing(sss)
        return rr
