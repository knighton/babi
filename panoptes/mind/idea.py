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
                 is_animate=None, selector=None, noun=None, rel2arg=None):
        if rel2arg:
            rel2arg = {}

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

        self.rel2arg = rel2arg
        if self.rel2arg:
            for rel, arg in self.rel2arg.iteritems():
                assert Relation.is_valid(rel)
                assert isinstance(arg, Idea)

    def relevance(self, view):
        return 0.0


class Clause(Idea):
    def __init__(self, status, purpose, is_intense, verb, re2arg):
        self.status = status
        assert Status.is_valid(self.status)

        self.purpose = purpose
        assert Purpose.is_valid(self.purpose)

        self.is_intense = is_intense
        assert isinstance(self.is_intense, bool)

        self.verb = verb
        assert isinstance(self.verb, DeepVerb)

        self.rel2arg = rel2arg
        for rel, arg in self.rel2arg.iteritems():
            assert Relation.is_valid(rel)
            assert isinstance(arg, Idea)

    def relevance(self, view):
        return 0.0


def idea_from_view(view):
    assert False
