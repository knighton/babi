from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.tree.deep.content_clause import Status
from panoptes.ling.verb.verb import DeepVerb
from panoptes.mind.idea.base import Idea


class Clause(Idea):
    def __init__(self, status=Status.ACTUAL, purpose=Purpose.INFO,
                 is_intense=False, verb=None, adverbs=None, rel2xxx=None):
        if rel2xxx is None:
            rel2xxx = {}
        if adverbs is None:
            adverbs = []

        self.status = status
        assert Status.is_valid(self.status)

        self.purpose = purpose
        assert Purpose.is_valid(self.purpose)

        self.is_intense = is_intense
        assert isinstance(self.is_intense, bool)

        self.verb = verb
        if self.verb:
            assert isinstance(self.verb, DeepVerb)

        self.adverbs = adverbs
        for s in self.adverbs:
            assert isinstance(s, str)

        self.rel2xxx = rel2xxx
        for rel, xxx in self.rel2xxx.items():
            assert Relation.is_valid(rel)
            assert isinstance(xxx, list)
            for xx in xxx:
                assert isinstance(xx, list)
                for x in xx:
                    assert isinstance(x, int)

    def dump(self):
        rel2xxx = {}
        for rel, xxx in self.rel2xxx.items():
            rel2xxx[Relation.to_str[rel]] = xxx
        return {
            'type': 'Clause',
            'status': Status.to_str[self.status],
            'purpose': Purpose.to_str[self.purpose],
            'is_intense': self.is_intense,
            'verb': self.verb.dump() if self.verb else None,
            'rel2xxx': rel2xxx,
        }

    def matches_clause_features(self, f, ideas):
        if self.purpose != Purpose.INFO:
            return False

        if self.verb.lemma not in f.possible_lemmas:
            return False

        for rel, want_xx in f.rel2xx.items():
            if rel not in self.rel2xxx:
                continue

            my_xxx = self.rel2xxx[rel]
            if want_xx not in my_xxx:
                return False

        return True


class ClauseFeatures(object):
    def __init__(self, possible_lemmas=None, rel2xx=None):
        if possible_lemmas is None:
            possible_lemmas = []
        if rel2xx is None:
            rel2xx = {}

        self.possible_lemmas = set(possible_lemmas)
        self.rel2xx = rel2xx

    def dump(self):
        rel2xx = {}
        for rel, xx in self.rel2xx.items():
            rel = Relation.to_str[rel]
            rel2xx[rel] = xx
        return {
            'possible_lemmas': sorted(self.possible_lemmas),
            'rel2xx': rel2xx,
        }
