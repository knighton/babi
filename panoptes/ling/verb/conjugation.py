from base.suffix_transform import SuffixTransform


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
