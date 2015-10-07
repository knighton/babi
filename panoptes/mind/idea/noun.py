from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Gender
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
                 rel2xx=None, carrying=None):
        if attributes is None:
            attributes = []
        if rel2xx is None:
            rel2xx = {}
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
            'query': Query.to_str[self.query] if self.query else None,
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'is_animate': self.is_animate,
            'attributes': self.attributes,
            'kind': self.kind,
            'rel2xx': rel2xx,
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

        for rel, xx in to.rel2xx:
            self.rel2xx[rel] = xx

        self.carrying = sorted(set(self.carrying + to.carrying))

        assert to.location_history.is_empty()

    def matches_noun_view(self, view, ideas, place_kinds):
        if self.query != view.query:
            return False

        # Otherwise we'll match indiscriminately.
        if view.name:
            if view.name != self.name:
                return False

        if view.gender and self.gender:
            if view.gender != self.gender:
                return False

        for s in view.attributes:
            if s not in self.attributes:
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
        return Noun(query=Query.IDENTITY, kind='person')

    @staticmethod
    def from_view(view):
        return Noun(query=view.query, name=view.name, gender=view.gender,
                    attributes=view.attributes, kind=view.kind)


class NounView(object):
    def __init__(self, query=None, name=None, gender=None, attributes=None,
                 kind=None):
        if attributes is None:
            attributes = []

        self.query = query
        self.name = name
        self.gender = gender
        self.attributes = attributes
        self.kind = kind

    def dump(self):
        return {
            'query': Query.to_str[self.query] if self.query else None,
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'attributes': self.attributes,
            'kind': self.kind,
        }
