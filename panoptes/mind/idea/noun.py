from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Gender
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea.base import Idea
from panoptes.mind.know.location import LocationHistory


# What about it?
#
# What we are looking up, if anything.
#
# If query is None, the Idea is an instance.
Query = enum('Query = CARDINALITY IDENTITY GENERIC')


class Noun(Idea):
    def __init__(self, query=None, name=None, gender=None,
                 is_animate=None, attributes=None, kind=None,
                 rel2xxx=None, carrying=None):
        if attributes is None:
            attributes = []
        if rel2xxx is None:
            rel2xxx = {}
        if carrying is None:
            carrying = []

        self.query = query
        if self.query:
            assert Query.is_valid(self.query)

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

        self.attributes = attributes
        assert isinstance(self.attributes, list)
        for s in self.attributes:
            assert s
            assert isinstance(s, basestring)

        self.kind = kind
        if self.kind:
            assert isinstance(self.kind, basestring)

        self.rel2xxx = rel2xxx
        for rel, xxx in self.rel2xxx.iteritems():
            assert Relation.is_valid(rel)
            assert isinstance(xxx, list)
            for xx in xxx:
                assert isinstance(xx, list)
                for x in xx:
                    assert isinstance(x, int)

        self.carrying = carrying
        for x in self.carrying:
            assert isinstance(x, int)

        self.location_history = LocationHistory()


    def dump(self):
        rel2xxx = {}
        for rel, xx in self.rel2xxx.iteritems():
            rel2xxx[Relation.to_str[rel]] = xxx
        return {
            'type': 'Noun',
            'query': Query.to_str[self.query] if self.query else None,
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'is_animate': self.is_animate,
            'attributes': self.attributes,
            'kind': self.kind,
            'rel2xxx': rel2xxx,
            'carrying': self.carrying,
            'location_history': self.location_history.dump(),
        }

    def assign(self, to):
        assert not self.query
        assert not to.query

        if to.name:
            self.name = to.name

        if to.gender:
            self.gender = to.gender

        if to.is_animate is not None:
            self.is_antimate = to.is_animate

        self.attributes = sorted(set(self.attributes + to.attributes))

        if to.kind:
            self.kind = to.kind

        for rel, xxx in to.rel2xxx:
            self.rel2xxx[rel] = xxx

        self.carrying = sorted(set(self.carrying + to.carrying))

        assert to.location_history.is_empty()

    def matches_noun_features(self, f, ideas, place_kinds):
        if self.query != f.query:
            return False

        # Otherwise we'll match indiscriminately.
        if f.name:
            if f.name != self.name:
                return False

        if f.gender and self.gender:
            if f.gender != self.gender:
                return False

        for s in f.attributes:
            if s not in self.attributes:
                return False

        if f.kind and self.kind:
            if f.kind == self.kind:
                pass
            elif f.kind == 'place' and self.kind in place_kinds:
                pass
            else:
                return False

        if self.rel2xxx != f.rel2xxx:
            return False

        return True

    @staticmethod
    def make_who():
        return Noun(query=Query.IDENTITY, kind='person')

    @staticmethod
    def from_features(f):
        return Noun(query=f.query, name=f.name, gender=f.gender,
                    attributes=f.attributes, kind=f.kind, rel2xxx=f.rel2xxx)


class NounFeatures(object):
    def __init__(self, query=None, name=None, gender=None, attributes=None,
                 kind=None, rel2xxx=None):
        if attributes is None:
            attributes = []
        if rel2xxx is None:
            rel2xxx = {}

        self.query = query
        self.name = name
        self.gender = gender
        self.attributes = attributes
        self.kind = kind
        self.rel2xxx = rel2xxx

    def dump(self):
        return {
            'query': Query.to_str[self.query] if self.query else None,
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'attributes': self.attributes,
            'kind': self.kind,
            'rel2xxx': self.rel2xxx,
        }
