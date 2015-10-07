from copy import deepcopy
import json

from panoptes.ling.glue.conjunction import Conjunction
from panoptes.ling.glue.grammatical_number import N5
from panoptes.ling.glue.inflection import Declension, Gender
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.morph.gender.gender import GenderClassifier
from panoptes.ling.tree.common.util.selector import Correlative
from panoptes.ling.tree.common.personal_pronoun import PersonalPronoun
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.common.time_of_day import TimeOfDay
from panoptes.ling.tree.deep.common_noun import DeepCommonNoun
from panoptes.ling.tree.deep.comparative import DeepComparative
from panoptes.ling.tree.deep.conjunction import DeepConjunction
from panoptes.ling.tree.deep.content_clause import DeepContentClause
from panoptes.ling.tree.deep.direction import DeepDirection
from panoptes.mind.know.graph import Graph
from panoptes.mind.idea import Clause, ClauseView, Comparative, Query, Noun, \
    NounView, NounReverb, idea_from_view, Direction, RelativeDay


class DeepReference(object):
    """
    Used in resolving DeepArguments.
    """

    def __init__(self, owning_clause_id, is_subj, arg):
        # We need to know if referents are from the same clause in order to
        # handle reflexives.
        self.owning_clause_id = owning_clause_id

        # Whether subject or not.  Needed for personal pronouns (I vs me).
        self.is_subj = is_subj

        # The actual argument.
        self.arg = arg


class IdeaReference(object):
    """
    Used in expressing Ideas.
    """

    def __init__(self, owning_clause_id, is_subj, xx):
        # Reflexives are intra-clause (eg, "You know you know yourself").
        self.owning_clause_id = owning_clause_id

        # Affects case (eg, "I" vs "me").
        self.is_subj = is_subj

        # Nonempty list of sorted, unique memory indexes (eg, "no one" is a
        # common noun where the correlative is NEG).
        self.xx = xx


class Memory(object):
    def __init__(self):
        self.ideas = []

        self.type2decode = {
            DeepCommonNoun: self.decode_common_noun,
            DeepComparative: self.decode_comparative,
            DeepConjunction: self.decode_conjunction,
            DeepContentClause: self.decode_content_clause,
            DeepDirection: self.decode_direction,
            PersonalPronoun: self.decode_personal_pronoun,
            ProperNoun: self.decode_proper_noun,
            TimeOfDay: self.decode_time_of_day,
        }

        self.next_clause_id = 0

        self.place_rels = set([
            Relation.PLACE,
            Relation.TO_LOCATION,
        ])

        self.place_kinds = set()

        self.gender_clf = GenderClassifier()

        self.graph = Graph()

    def make_checkpoint(self):
        return deepcopy(self)

    def load_checkpoint(self, checkpoint):
        """
        This doesn't work!

        for attr in dir(checkpoint):
            if attr.startswith('__'):
                continue
            setattr(self, attr, getattr(checkpoint, attr))
        """
        self.ideas = checkpoint.ideas
        self.type2decode = checkpoint.type2decode
        self.next_clause_id = checkpoint.next_clause_id
        self.place_rels = checkpoint.place_rels
        self.place_kinds = checkpoint.place_kinds
        self.gender_clf = checkpoint.gender_clf
        self.graph = checkpoint.graph

    def show(self):
        print '=' * 80
        print 'Memory'
        print '-' * 80
        for i, idea in enumerate(self.ideas):
            print '\t\t[%d]' % i
            if idea:
                print json.dumps(idea.dump(), indent=4, sort_keys=True)
        print '=' * 80

    def new_clause_id(self):
        r = self.next_clause_id
        self.next_clause_id += 1
        return r

    def add_idea(self, idea):
        x = len(self.ideas)
        self.ideas.append(idea)
        return x

    def go_to_the_source(self, x):
        while True:
            idea = self.ideas[x]
            if not isinstance(idea, NounReverb):
                break
            x = idea.x
        return x

    def resolve_one_noun(self, view):
        for i in xrange(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_noun_view(view, self.ideas, self.place_kinds):
                idea = NounReverb(i)
                x = self.add_idea(idea)
                x = self.go_to_the_source(x)
                return [x]

        idea = idea_from_view(view)
        x = self.add_idea(idea)
        return [x]

    def resolve_plural_noun(self, view):
        rr = []
        for i in xrange(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_noun_view(view, self.ideas, self.place_kinds):
                idea = NounReverb(i)
                x = self.add_idea(idea)
                x = self.go_to_the_source(x)
                rr.append(x)
                if 1 < len(rr):
                    return rr

        idea = idea_from_view(view)
        x = self.add_idea(idea)
        return [x]

    def resolve_one_clause(self, view):
        for i in xrange(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_clause_view(view):
                return i

        return None

    def decode_conjunction(self, deep_ref, from_xx, to_xx):
        xxx = []
        for a in deep_ref.arg.aa:
            sub_deep_ref = DeepReference(
                owning_clause_id=deep_ref.owning_clause_id,
                is_subj=deep_ref.is_subj, arg=a)
            xx = self.decode(sub_deep_ref, from_xx, to_xx)
            xxx.append(xx)

        if deep_ref.arg.op == Conjunction.ALL_OF:
            xx = reduce(lambda a, b: a + b, xxx)
            return sorted(set(xx))
        else:
            return xxx[0]

    def decode_common_noun(self, deep_ref, from_xx, to_xx):
        n = deep_ref.arg

        assert not n.possessor
        assert not n.rels_nargs

        if n.number and n.number.is_interrogative():
            assert n.selector.correlative == Correlative.INDEF
            idea = Noun(query=Query.CARDINALITY, attributes=n.attributes,
                        kind=n.noun)
            x = self.add_idea(idea)
            return [x]

        if n.selector.correlative == Correlative.INDEF:
            if n.selector.n_min == N5.SING and n.selector.n_max == N5.SING:
                # Create a new one.
                idea = Noun(attributes=n.attributes, kind=n.noun)
                x = self.add_idea(idea)
                return [x]
            elif N5.DUAL <= n.selector.n_min:
                # It's referring to all of instances with those fields.
                view = NounView(query=Query.GENERIC, attributes=n.attributes,
                                kind=n.noun)
                xx = self.resolve_one_noun(view)
                return xx
            else:
                assert False

        assert n.selector.correlative in [
            Correlative.DEF,
            Correlative.DIST,
            Correlative.INTR,
        ]

        if n.selector.correlative == Correlative.INTR:
            idea = Noun(query=Query.IDENTITY, attributes=n.attributes,
                        kind=n.noun)
            x = self.add_idea(idea)
            return [x]

        d = n.selector.dump()
        del d['correlative']
        if d != {
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        }:
            return []

        if n.noun == 'person':
            gender = None
        else:
            gender = Gender.NEUTER
        view = NounView(attributes=n.attributes, kind=n.noun, gender=gender)
        return self.resolve_one_noun(view)

    def decode_comparative(self, deep_ref, from_xx, to_xx):
        sub_deep_ref = DeepReference(
            owning_clause_id=deep_ref.owning_clause_id, is_subj=False,
            arg=deep_ref.arg.than)
        sub_xx = self.decode(sub_deep_ref, from_xx, to_xx)
        rr = []
        for sub_x in sub_xx:
            deep = deep_ref.arg
            comp = Comparative(deep.polarity, deep.adjective, sub_x)
            x = self.add_idea(comp)
            rr.append(x)
        return rr

    def decode_content_clause(self, deep_ref, from_xx, to_xx):
        c = deep_ref.arg

        # We use the clause ID to tell decode reflexives and so on recursively.
        clause_id = self.new_clause_id()

        # Translate each verb argument to a list of memory indexes.
        rel2xx = {}
        for i, (rel, varg) in enumerate(c.rels_vargs):
            is_subj = i == c.subj_index
            deep_ref = DeepReference(clause_id, is_subj, varg)
            xx = self.decode(deep_ref, from_xx, to_xx)
            if xx is None:
                return None

            # Learn "places".
            if rel in self.place_rels:
                for x in xx:
                    idea = self.ideas[x]
                    if isinstance(idea, Noun):
                        if not idea.kind:
                            continue
                        self.place_kinds.add(idea.kind)

            assert xx
            rel2xx[rel] = xx

        # The rest are unchanged in the conversion to memory.
        idea = Clause(c.status, c.purpose, c.is_intense, c.verb, c.adverbs,
                      rel2xx)

        x = self.add_idea(idea)
        return [x]

    def decode_direction(self, deep_ref, from_xx, to_xx):
        sub_deep_ref = DeepReference(
            owning_clause_id=deep_ref.owning_clause_id, is_subj=False,
            arg=deep_ref.arg.of)
        sub_xx = self.decode(sub_deep_ref, from_xx, to_xx)
        rr = []
        for sub_x in sub_xx:
            dr = Direction(deep_ref.arg.which, sub_x)
            x = self.add_idea(dr)
            rr.append(x)
        return rr

    def decode_personal_pronoun(self, deep_ref, from_xx, to_xx):
        d = deep_ref.arg.declension

        if d == Declension.WHO1:
            who = Noun.make_who()
            x = self.add_idea(who)
            return [x]
        elif d == Declension.WHO2:
            who = Noun.make_who()
            x = self.add_idea(who)
            return [x]
        elif d == Declension.YOU:
            return to_xx
        elif d == Declension.HE:
            view = NounView(gender=Gender.MALE, kind='person')
        elif d == Declension.SHE:
            view = NounView(gender=Gender.FEMALE, kind='person')
        elif d == Declension.THEY2:
            view = NounView(kind='person')
            return self.resolve_plural_noun(view)
        else:
            print 'Unhandled declension, bailing on this dsen:', \
                Declension.to_str[d]
            return None

        return self.resolve_one_noun(view)

    def decode_proper_noun(self, deep_ref, from_xx, to_xx):
        name = deep_ref.arg.name
        gender = self.gender_clf.classify(name)
        view = NounView(name=name, gender=gender)
        return self.resolve_one_noun(view)

    def decode_time_of_day(self, deep_ref, from_xx, to_xx):
        t = deep_ref.arg
        n = RelativeDay(t.day_offset, t.section)
        x = self.add_idea(n)
        return [x]

    def decode(self, deep_ref, from_xx, to_xx):
        """
        (DeepReference, from_xx, to_xx) -> xx
        """
        f = self.type2decode[type(deep_ref.arg)]
        return f(deep_ref, from_xx, to_xx)

    def decode_dsen(self, dsen, from_xx, to_xx):
        deep_ref = DeepReference(
            owning_clause_id=None, is_subj=False, arg=dsen.root)
        return self.decode(deep_ref, from_xx, to_xx)


"""
    def are_singular(self, xx):
        if len(xx) != 1:
            return False

        x, = xx
        return self.items[x].is_singular()

    def get_activated(self, is_singular, is_animate, gender):
        assert False  # XXX

    def decode_personal_pronoun(self, deep_ref, from_xx, to_xx):
        arg = deep_ref.arg

        if arg.is_interrogative():
            who = make_who()
            x = self.add_item(who)
            return [x]

        previously_in_clause = arg.ppcase = PersonalPronounCase.REFLEXIVE

        d = args.declension

        if d == Declension.I:
            if not self.are_singular(from_xx):
                return []
            xxx = [from_xx]
        elif d == Declension.WE:
            xxx = []
            for me in [[], from_xx]:
                for you in [[], to_xx]:
                    for other in self.get_activated(None, None, None):
                        xx = me + you + other
                        if self.are_singular(xx):
                            continue
                        xxx.append(xx)
        elif d == Declension.YOU:
            if not self.are_singular(to_xx):
                return []
            xxx = [to_xx]
        elif d == Declension.YALL:
            if self.are_singular(to_xx):
                return []
            xxx = [to_xx]
            for other in self.get_activated(None, None, None):
                xxx.append(to_xx + other)
        elif d == Declension.HE:
            xxx = self.get_activated(True, True, Gender.MALE)
        elif d == Declension.SHE:
            xxx = self.get_activated(True, True, Gender.FEMALE)
        elif d == Declension.IT:
            xxx = self.get_activated(True, False, Gender.NEUTER)
        elif d == Declension.THEY1:
            xxx = self.get_activated(True, True, None)
        elif d == Declension.ONE:
            xxx = self.get_activated(True, True, None)
        elif d == Declension.THEY2:
            xxx = self.get_activated(False, None, None)
        else:
            assert False

        return xxx
"""