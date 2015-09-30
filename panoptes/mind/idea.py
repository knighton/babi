from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Gender
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.tree.common.util.selector import Selector
from panoptes.ling.tree.deep.content_clause import Status
from panoptes.ling.verb.verb import DeepVerb


class View(object):
    def __init__(self, name=None, noun=None):
        self.name = name
        self.noun = noun

    def dump(self):
        return {
            'name': self.name,
            'noun': self.noun,
        }


class Idea(object):
    def relevance(self, view):
        """
        Gloss -> float in [0.0, 1.0]

        Returns how well the view matches this object.  Used for reference
        resolution.
        """
        raise NotImplementedError


Identity = enum('Identity = GIVEN REQUESTED')


class Noun(Idea):
    def __init__(self, identity=Identity.GIVEN, name=None, gender=None,
                 is_animate=None, selector=None, noun=None, rel2xx=None,
                 location=None, carrying=None):
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

        self.noun = noun
        if self.noun:
            assert isinstance(self.noun, basestring)

        self.rel2xx = rel2xx
        for rel, x in self.rel2xx.iteritems():
            assert Relation.is_valid(rel)
            assert isinstance(xx, list)
            for x in xx:
                assert isinstance(x, int)

        self.location = location
        if self.location is not None:
            assert isinstance(self.location, int)

        self.carrying = carrying
        for x in self.carrying:
            assert isinstance(x, int)

    def dump(self):
        rel2xx = {}
        for rel, xx in self.rel2xx.iteritems():
            rel2xx[Relation.to_str[rel]] = xx
        return {
            'identity': Identity.to_str[self.identity],
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'is_animate': self.is_animate,
            'selector': self.selector.dump() if self.selector else None,
            'noun': self.noun,
            'rel2xx': rel2xx,
            'location': self.location,
            'carrying': self.carrying,
        }

    def matches(self, view):
        match = False

        if view.name and self.name:
            if view.name == self.name:
                match = True
            else:
                return False

        if view.noun and self.noun:
            if view.noun == self.noun:
                match = True
            else:
                return False

        return match


class Clause(Idea):
    def __init__(self, status=Status.ACTUAL, purpose=Purpose.INFO,
                 is_intense=False, verb=None, rel2xx=None):
        if rel2xx is None:
            rel2xx = {}

        self.status = status
        assert Status.is_valid(self.status)

        self.purpose = purpose
        assert Purpose.is_valid(self.purpose)

        self.is_intense = is_intense
        assert isinstance(self.is_intense, bool)

        self.verb = verb
        if self.verb:
            assert isinstance(self.verb, DeepVerb)

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
            'status': Status.to_str[self.status],
            'purpose': Purpose.to_str[self.purpose],
            'is_intense': self.is_intense,
            'verb': self.verb.dump() if self.verb else None,
            'rel2xx': rel2xx,
        }

    def matches(self, view):
        return False


def idea_from_view(view):
    print 'IDEA FROM VIEW', view.dump()
    return Noun(name=view.name, noun=view.noun)
