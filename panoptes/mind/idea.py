from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Gender
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.tree.common.util.selector import Selector
from panoptes.ling.tree.deep.content_clause import Status
from panoptes.ling.verb.verb import DeepVerb
from panoptes.mind.location import LocationHistory


class Idea(object):
    def dump(self):
        raise NotImplementedError

    def matches_noun_view(self, view, ideas, place_kinds):
        return False

    def matches_clause_view(self, view):
        return False


Identity = enum('Identity = GIVEN REQUESTED')


class Noun(Idea):
    def __init__(self, identity=Identity.GIVEN, name=None, gender=None,
                 is_animate=None, selector=None, kind=None, rel2xx=None,
                 carrying=None):
        if rel2xx is None:
            rel2xx = {}
        if carrying is None:
            carrying = []

        self.identity = identity
        assert Identity.is_valid(self.identity)

        self.name = name
        if self.name is not None:
            assert self.name
            assert isinstance(self.name, tuple)

        self.gender = gender
        if self.gender:
            assert Gender.is_valid(self.gender)

        self.is_animate = is_animate
        if self.is_animate:
            assert isinstance(self.is_animate, bool)

        self.selector = selector
        if self.selector:
            assert isinstance(self.selector, Selector)

        self.kind = kind
        if self.kind:
            assert isinstance(self.kind, basestring)

        self.rel2xx = rel2xx
        for rel, x in self.rel2xx.iteritems():
            assert Relation.is_valid(rel)
            assert isinstance(xx, list)
            for x in xx:
                assert isinstance(x, int)

        self.carrying = carrying
        for x in self.carrying:
            assert isinstance(x, int)

        self.location_history = LocationHistory()


    def dump(self):
        rel2xx = {}
        for rel, xx in self.rel2xx.iteritems():
            rel2xx[Relation.to_str[rel]] = xx
        return {
            'type': 'Noun',
            'identity': Identity.to_str[self.identity],
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'is_animate': self.is_animate,
            'selector': self.selector.dump() if self.selector else None,
            'kind': self.kind,
            'rel2xx': rel2xx,
            'carrying': self.carrying,
            'location_history': self.location_history.dump(),
        }

    def matches_noun_view(self, view, ideas, place_kinds):
        if self.identity == Identity.REQUESTED:
            return False

        # Otherwise we'll match indiscriminately.
        if view.name:
            if view.name != self.name:
                return False

        if view.gender and self.gender:
            if view.gender != self.gender:
                return False

        if view.kind and self.kind:
            if view.kind == self.kind:
                pass
            elif view.kind == 'place' and self.kind in place_kinds:
                pass
            else:
                return False

        return True

    @staticmethod
    def make_who():
        return Noun(identity=Identity.REQUESTED, name=None, gender=None,
                    is_animate=None, selector=None, kind='person', rel2xx=None,
                    carrying=None)


class NounReverb(Idea):
    """
    Points back to an earlier idea.

    We create a new object for each new reference to the same earlier object in
    order for coreference resolution to work, which often depends on how "hot"
    references are.
    """

    def __init__(self, x):
        self.x = x

    def dump(self):
        return {
            'type': 'NounReverb',
            'x': self.x,
        }

    def matches_noun_view(self, view, ideas, place_kinds):
        n = ideas[self.x]
        return n.matches_noun_view(view, ideas, place_kinds)


class NounView(object):
    def __init__(self, name=None, gender=None, kind=None):
        self.name = name
        self.gender = gender
        self.kind = kind

    def dump(self):
        return {
            'name': self.name,
            'gender': Gender.to_str[self.gender],
            'kind': self.kind,
        }


def idea_from_view(view):
    print 'IDEA FROM VIEW', view.dump()
    return Noun(name=view.name, gender=view.gender, kind=view.kind)


class Direction(Idea):
    def __init__(self, which, of_x):
        self.which = which
        self.of_x = of_x

    def dump(self):
        return {
            'type': 'Direction',
            'which': self.which,
            'of_x': self.of_x,
        }



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
