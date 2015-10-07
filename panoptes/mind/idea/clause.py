from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.tree.deep.content_clause import Status
from panoptes.ling.verb.verb import DeepVerb
from panoptes.mind.idea.base import Idea


class Clause(Idea):
    def __init__(self, status=Status.ACTUAL, purpose=Purpose.INFO,
                 is_intense=False, verb=None, adverbs=None, rel2xx=None):
        if rel2xx is None:
            rel2xx = {}
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
            assert isinstance(s, basestring)

        self.rel2xx = rel2xx
        for rel, xx in self.rel2xx.iteritems():
            assert Relation.is_valid(rel)
            assert isinstance(xx, list)
            for x in xx:
                assert isinstance(x, int)

    def dump(self):
        rel2xx = {}
        for rel, xx in self.rel2xx.iteritems():
            rel2xx[Relation.to_str[rel]] = xx
        return {
            'type': 'Clause',
            'status': Status.to_str[self.status],
            'purpose': Purpose.to_str[self.purpose],
            'is_intense': self.is_intense,
            'verb': self.verb.dump() if self.verb else None,
            'rel2xx': rel2xx,
        }

    def matches_clause_view(self, view):
        if self.purpose != Purpose.INFO:
            return False

        if self.verb.lemma not in view.possible_lemmas:
            return False

        for rel, want_xx in view.rel2xx.iteritems():
            if rel not in self.rel2xx:
                continue

            my_xx = self.rel2xx[rel]
            if want_xx != my_xx:
                return False

        return True


class ClauseView(object):
    def __init__(self, possible_lemmas=None, rel2xx=None):
        if possible_lemmas is None:
            possible_lemmas = []
        if rel2xx is None:
            rel2xx = {}

        self.possible_lemmas = set(possible_lemmas)
        self.rel2xx = rel2xx

    def dump(self):
        rel2xx = {}
        for rel, xx in self.rel2xx.iteritems():
            rel = Relation.to_str[rel]
            rel2xx[rel] = xx
        return {
            'possible_lemmas': sorted(self.possible_lemmas),
            'rel2xx': rel2xx,
        }
