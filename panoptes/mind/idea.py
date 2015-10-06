from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Gender
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.morph.comparative.comparative import ComparativePolarity
from panoptes.ling.tree.common.time_of_day import DaySection
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


# What we are looking up, if anything.
#
# If query is None, the Idea is data.
Query = enum('Query = CARDINALITY IDENTITY')


class Noun(Idea):
    def __init__(self, query=None, name=None, gender=None,
                 is_animate=None, selector=None, attributes=None, kind=None,
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

        self.selector = selector
        if self.selector:
            assert isinstance(self.selector, Selector)

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
            'selector': self.selector.dump() if self.selector else None,
            'attributes': self.attributes,
            'kind': self.kind,
            'rel2xx': rel2xx,
            'carrying': self.carrying,
            'location_history': self.location_history.dump(),
        }

    def matches_noun_view(self, view, ideas, place_kinds):
        if self.query:
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
    def __init__(self, name=None, gender=None, attributes=None, kind=None):
        if attributes is None:
            attributes = []

        self.name = name
        self.gender = gender
        self.attributes = attributes
        self.kind = kind

    def dump(self):
        return {
            'name': self.name,
            'gender': Gender.to_str[self.gender] if self.gender else None,
            'attributes': self.attributes,
            'kind': self.kind,
        }


def idea_from_view(view):
    print 'IDEA FROM VIEW', view.dump()
    return Noun(name=view.name, gender=view.gender, attributes=view.attributes,
                kind=view.kind)


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


class Comparative(Idea):
    def __init__(self, polarity, adjective, than_x):
        self.polarity = polarity
        self.adjective = adjective
        self.than_x = than_x

    def dump(self):
        return {
            'type': 'Comparative',
            'polarity': ComparativePolarity.to_str[self.polarity],
            'adjective': self.adjective,
            'than_x': self.than_x,
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

    def dump(self):
        rel2xx = {}
        for rel, xx in self.rel2xx.iteritems():
            rel = Relation.to_str[rel]
            rel2xx[rel] = xx
        return {
            'possible_lemmas': sorted(self.possible_lemmas),
            'rel2xx': rel2xx,
        }


class RelativeDay(Idea):
    def __init__(self, day_offset, section):
        self.day_offset = day_offset
        assert isinstance(self.day_offset, int)

        self.section = section
        if self.section:
            assert DaySection.is_valid(self.section)

    def dump(self):
        section = DaySection.to_str[self.section] if self.section else None
        return {
            'type': 'RelativeDay',
            'day_offset': self.day_offset,
            'section': section,
        }

    def to_time_span(self):
        a = self.day_offset * len(DaySection.values)
        if self.section:
            a += self.section - DaySection.first
            z = a
        else:
            z = a + len(DaySection.values) - 1
        return a, z
