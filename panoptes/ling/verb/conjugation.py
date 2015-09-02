from base.suffix_transform import SuffixTransform
from base.suffix_generalizing_map import SuffixGeneralizingMap
from ling.verb.annotation import annotate_as_aux


MAGIC_INTS_LEMMA = '<ints>'


class ConjugationMap(object):
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
        return ConjugationMap(
            self.lemma, self.pres_part, self.past_part,
            map(annotate_as_aux, self.nonpast), map(annotate_as_aux, self.past))


def conjugations_from_file(fn):
    rr = []
    with open(fn) as f:
        for line in f:
            ss = map(lambda s: s if '|' not in s else s.split('|'),
                     line.split())
            r = ConjugationMap(*ss)
            rr.append(r)
    return rr


class ConjugationMapDerivation(object):
    """
    Mapping of lemma -> ConjugationMap.  A set of transformations on a lemma.
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
    def from_conjugation_map(conj_map, suffix_transform_cache):
        def get(transform_to):
            return suffix_transform_cache.get(conj_map.lemma, transform_to)

        pres_part = get(conj_map.pres_part)
        past_part = get(conj_map.past_part)
        nonpast = map(get, conj_map.nonpast)
        past = map(get, conj_map.past)
        return ConjugationMap(lemma, pres_part, past_part, nonpast, past)

    def to_d(self):
        return {
            'pres_part': self.pres_part.to_d(),
            'past_part': self.past_part.to_d(),
            'nonpast': map(lambda t: t.to_d(), self.nonpast),
            'past': map(lambda t: t.to_d(), self.past),
        }

    def derive_conjugation_map(self, lemma):
        pres_part = self.pres_part.transform(lemma)
        past_part = self.past_part.transform(lemma)
        nonpast = map(lambda t: t.transform(lemma), self.nonpast)
        past = map(lambda t: t.transform(lemma), self.past)
        return ConjugationMap(lemma, pres_part, past_part, nonpast, past)

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


def collect_conjugation_map_derivations(vv):
    # List the unique conjugation map derivations, and the verbs handled by each
    # derivation.
    transform_cache = SuffixTransformCache()
    unique_derivs = []
    s2lemmas = defaultdict(set)
    for v in vv:
        deriv = \
            ConjugationMapDerivation.from_conjugation_map(v, transform_cache)
        s = str(deriv.to_d())
        if s not in s2lemmas:
            unique_derivs.append(d)
        assert v.lemma not in s2lemmas[s]
        s2lemmas[s].add(v.lemma)

    # Reorder by usage.
    counts_derivs = []
    for d in unique_derivs:
        s = str(d.to_d())
        count = len(s2lemmas[s])
        counts_derivs.append((count, d))
    counts_derivs.sort(reverse=True)
    derivs = map(lambda (c, d): d, counts_derivs)

    # Build verb -> derivation mapping.
    lemma2deriv_index = {}
    for i, d in enumerate(derivs):
        s = str(t.to_d())
        for lemma in s2lemmas[s]:
            assert lemma not in lemma2deriv_index
            lemma2deriv_index[lemma] = i

    return derivs, lemma2deriv_index


class Conjugator(object):
    """
    Conjugates and un-conjugates verbs.
    """

    def __init__(self, conj_maps):
        """
        list of ConjugationMap ->
        """
        self.derivs, self.lemma2deriv_index = \
            collect_verb_derivations(conj_maps)

        self.deriv_index_picker = \
            SuffixGeneralizingMap(self.lemma2deriv_index, min)

        self.to_be = self.derive_conjugation_map('be')
        self.to_have = self.derive_conjugation_map('have').annotated_as_aux()
        self.to_do = self.derive_conjugation_map('do')

    def derive_conjugation_map(self, lemma):
        conj_map = self.conj_map_cache.get(lemma)
        if conj_map:
            return conj_map

        if lemma == MAGIC_INTS_LEMMA:
            conj_map = ConjugationMap(
                '0', '1', '2', map(str, range(3, 3 + 6)),
                map(str, range(9, 9 + 6)))
        else:
            deriv_index = self.deriv_index_picker.get(lemma)
            d = self.derivs[deriv_index]
            conj_map = d.derive_conjugation_map(lemma)
        self.conj_map_cache[lemma] = conj_map
        return conj_map


