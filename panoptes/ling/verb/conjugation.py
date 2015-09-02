from collections import defaultdict

from base.suffix_transform import SuffixTransform
from base.suffix_generalizing_map import SuffixGeneralizingMap
from ling.verb.annotation import annotate_as_aux


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
        return Verb(self.lemma, self.pres_part, self.past_part,
                    map(annotate_as_aux, self.nonpast),
                    map(annotate_as_aux, self.past))


def conjugations_from_file(fn):
    rr = []
    with open(fn) as f:
        for line in f:
            ss = map(lambda s: s if '|' not in s else s.split('|'),
                     line.split())
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


class VerbDeriver(object):
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
        nonpast = map(t, verb.nonpast)
        past = map(t, verb.past)
        return Verb(verb.lemma, pres_part, past_part, nonpast, past)

    def to_d(self):
        return {
            'pres_part': self.pres_part.to_d(),
            'past_part': self.past_part.to_d(),
            'nonpast': map(lambda t: t.to_d(), self.nonpast),
            'past': map(lambda t: t.to_d(), self.past),
        }

    def derive_verb(self, lemma):
        pres_part = self.pres_part.transform(lemma)
        past_part = self.past_part.transform(lemma)
        nonpast = map(lambda t: t.transform(lemma), self.nonpast)
        past = map(lambda t: t.transform(lemma), self.past)
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
        deriv = VerbDeriver.from_verb(v, transform_cache)
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

    def __init__(self, verbs):
        """
        list of Verb ->
        """
        self.derivs, self.lemma2deriv_index = collect_verb_derivations(verbs)

        self.deriv_index_picker = \
            SuffixGeneralizingMap(self.lemma2deriv_index, min)

        self.to_be = self.derive_verb('be')
        self.to_have = self.derive_verb('have').annotated_as_aux()
        self.to_do = self.derive_verb('do')

    def derive_verb(self, lemma):
        verb = self.verb_cache.get(lemma)
        if verb:
            return verb

        if lemma == MAGIC_INTS_LEMMA:
            verb = Verb('0', '1', '2', map(str, range(3, 3 + 6)),
                        map(str, range(9, 9 + 6)))
        else:
            deriv_index = self.deriv_index_picker.get(lemma)
            d = self.derivs[deriv_index]
            verb = d.derive_verb(lemma)
        self.verb_cache[lemma] = verb
        return verb
