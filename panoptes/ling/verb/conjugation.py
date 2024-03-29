from collections import defaultdict

from panoptes.etc.suffix_transform import SuffixTransform
from panoptes.etc.suffix_generalizing_map import SuffixGeneralizingMap
from panoptes.ling.verb.annotation import annotate_as_aux


MAGIC_INTS_LEMMA = '<ints>'


class Verb(object):
    """
    Object that knows all the inflections of a verb.
    """

    def __init__(self, lemma, pres_part, past_part, nonpast, past):
        # Lemma (go).
        self.lemma = lemma
        assert self.lemma
        assert isinstance(self.lemma, str)

        # Present and past participles (going, gone).
        self.pres_part = pres_part
        self.past_part = past_part
        assert self.pres_part
        assert isinstance(self.pres_part, str)
        assert self.past_part
        assert isinstance(self.past_part, str)

        # Six nonpast, six past conjugations (3 persons x 2 numbers) (indicative
        # mood) (go, goes, went).
        self.nonpast = nonpast
        self.past = past
        assert len(self.nonpast) == 6
        for s in self.nonpast:
            assert s
            assert isinstance(s, str)
        assert len(self.past) == 6
        for s in self.past:
            assert s
            assert isinstance(s, str)

    def has_do_support(self):
        return self.lemma != 'be'

    def annotated_as_aux(self):
        """
        Tell auxiliary 'have' apart from regular 'have' because one of them
        forms contractions and the other doens't.
        """
        lemma = annotate_as_aux(self.lemma)
        nonpast = list(map(annotate_as_aux, self.nonpast))
        past = list(map(annotate_as_aux, self.past))
        return Verb(lemma, self.pres_part, self.past_part, nonpast, past)

    def dump(self):
        return {
            'lemma': self.lemma,
            'pres_part': self.pres_part,
            'past_part': self.past_part,
            'nonpast': self.nonpast,
            'past': self.past,
        }


def conjugations_from_file(fn):
    rr = []
    with open(fn) as f:
        for line in f:
            ss = [s if '|' not in s else s.split('|') for s in line.split()]
            r = Verb(*ss)
            rr.append(r)
    return rr


class SuffixTransformCache(object):
    """
    Computing these is (a) nontrivial and (b) sometimes repetitive, and (c) the
    results are not modified.
    """

    def __init__(self):
        self.key2transform = {}

    def get(self, before, after):
        key = (before, after)
        if key not in self.key2transform:
            self.key2transform[key] = \
                SuffixTransform.from_before_after(before, after)
        return self.key2transform[key]


class VerbDerivation(object):
    """
    A set of transformations on a lemma.
    """

    def __init__(self, pres_part, past_part, nonpast, past):
        self.pres_part = pres_part
        self.past_part = past_part
        assert isinstance(self.pres_part, SuffixTransform)
        assert isinstance(self.past_part, SuffixTransform)

        self.nonpast = nonpast
        self.past = past
        assert len(self.nonpast) == 6
        for t in self.nonpast:
            assert isinstance(t, SuffixTransform)
        assert len(self.past) == 6
        for t in self.past:
            assert isinstance(t, SuffixTransform)

    @staticmethod
    def from_verb(verb, suffix_transform_cache):
        def t(transform_to):
            return suffix_transform_cache.get(verb.lemma, transform_to)

        pres_part = t(verb.pres_part)
        past_part = t(verb.past_part)
        nonpast = list(map(t, verb.nonpast))
        past = list(map(t, verb.past))
        return VerbDerivation(pres_part, past_part, nonpast, past)

    def to_d(self):
        return {
            'pres_part': self.pres_part.to_d(),
            'past_part': self.past_part.to_d(),
            'nonpast': [t.to_d() for t in self.nonpast],
            'past': [t.to_d() for t in self.past],
        }

    def derive_verb(self, lemma):
        pres_part = self.pres_part.transform(lemma)
        past_part = self.past_part.transform(lemma)
        nonpast = [t.transform(lemma) for t in self.nonpast]
        past = [t.transform(lemma) for t in self.past]
        return Verb(lemma, pres_part, past_part, nonpast, past)

    def identify_word(self, conjugated):
        rr = []

        s = self.pres_part.inverse_transform(conjugated)
        if s:
            rr.append((s, 1))

        s = self.past_part.inverse_transform(conjugated)
        if s:
            rr.append((s, 2))

        for i, t in enumerate(self.nonpast):
            s = t.inverse_transform(conjugated)
            if s:
                rr.append((s, i + 3))

        for i, t in enumerate(self.past):
            s = t.inverse_transform(conjugated)
            if s:
                rr.append((s, i + 9))

        return rr


def collect_verb_derivations(vv):
    # List the unique conjugation map derivations, and the verbs handled by each
    # derivation.
    transform_cache = SuffixTransformCache()
    unique_derivs = []
    s2lemmas = defaultdict(set)
    for v in vv:
        deriv = VerbDerivation.from_verb(v, transform_cache)
        s = str(deriv.to_d())
        if s not in s2lemmas:
            unique_derivs.append(deriv)
        assert v.lemma not in s2lemmas[s]
        s2lemmas[s].add(v.lemma)

    # Reorder by usage.
    counts_strs_derivs = []
    for d in unique_derivs:
        s = str(d.to_d())
        count = len(s2lemmas[s])
        counts_strs_derivs.append((count, s, d))
    counts_strs_derivs.sort(reverse=True)
    derivs = [csd[2] for csd in counts_strs_derivs]

    # Build verb -> derivation mapping.
    lemma2deriv_index = {}
    for i, deriv in enumerate(derivs):
        s = str(deriv.to_d())
        for lemma in s2lemmas[s]:
            assert lemma not in lemma2deriv_index
            lemma2deriv_index[lemma] = i

    return derivs, lemma2deriv_index


class Conjugator(object):
    """
    Conjugates and un-conjugates verbs.
    """

    def __init__(self, verbs):
        self.identify_word_cache = {}
        self.verb_cache = {}

        self.verb_derivations, self.lemma2deriv_index = \
            collect_verb_derivations(verbs)

        self.deriv_index_picker = \
            SuffixGeneralizingMap(self.lemma2deriv_index, min)

    @staticmethod
    def from_file(f):
        vv = conjugations_from_file(f)
        return Conjugator(vv)

    def create_verb(self, lemma):
        """
        lemma -> Verb
        """
        verb = self.verb_cache.get(lemma)
        if verb:
            return verb

        if lemma == MAGIC_INTS_LEMMA:
            verb = Verb('0', '1', '2', list(map(str, list(range(3, 3 + 6)))),
                        list(map(str, list(range(9, 9 + 6)))))
        else:
            deriv_index = self.deriv_index_picker.get(lemma)
            deriv = self.verb_derivations[deriv_index]
            verb = deriv.derive_verb(lemma)
        self.verb_cache[lemma] = verb
        return verb

    def identify_word(self, word, is_picky_about_verbs=True):
        """
        conjugated word, is picky -> list of (lemma, verb field index)
        """
        key = (word, is_picky_about_verbs)
        lemmas_indexes = self.identify_word_cache.get(key)
        if lemmas_indexes is not None:
            return lemmas_indexes

        # For each verb derivation, undo the conjugation in order to get the
        # hypothetical original lemma.
        #
        # If the generalizing suffix map picks the same verb derivation we used
        # for that lemma, it's a match.
        lemmas_indexes = []
        for i, deriv in enumerate(self.verb_derivations):
            for lemma, field_index in deriv.identify_word(word):
                if self.deriv_index_picker.get(lemma) == i:
                    lemmas_indexes.append((lemma, field_index))

        # If we're picky, and we have some results that contain known verbs,
        # forget about the results with unknown verbs.
        if is_picky_about_verbs:
            has_known = False
            for lemma, field_index in lemmas_indexes:
                if lemma in self.lemma2deriv_index:
                    has_known = True
                    break
            if has_known:
                lemmas_indexes = [lemma_index for lemma_index in lemmas_indexes if lemma_index[0] in self.lemma2deriv_index]

        lemmas_indexes.append((word, 0))

        key = (word, is_picky_about_verbs)
        self.identify_word_cache[key] = lemmas_indexes
        return lemmas_indexes
