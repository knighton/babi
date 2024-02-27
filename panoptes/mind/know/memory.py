from copy import deepcopy
import json

from panoptes.ling.glue.conjunction import Conjunction
from panoptes.ling.glue.grammatical_number import N5
from panoptes.ling.glue.inflection import Declension, Gender
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.morph.gender.gender import GenderClassifier
from panoptes.ling.tree.common.adjective import Adjective
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
from panoptes.mind.idea.clause import Clause, ClauseFeatures
from panoptes.mind.idea.comparative import Comparative
from panoptes.mind.idea.direction import Direction
from panoptes.mind.idea.noun import Noun, NounFeatures, Query
from panoptes.mind.idea.reverb import Reverb
from panoptes.mind.idea.time import RelativeDay
from functools import reduce


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
            Adjective: self.decode_adjective,
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
        print('=' * 80)
        print('Memory')
        print('-' * 80)
        for i, idea in enumerate(self.ideas):
            print('\t\t[%d]' % i)
            if idea:
                print(json.dumps(idea.dump(), indent=4, sort_keys=True))
        print('=' * 80)

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
            if not isinstance(idea, Reverb):
                break
            x = idea.x
        return x

    def resolve_one_noun(self, features):
        for i in range(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_noun_features(
                    features, self.ideas, self.place_kinds):
                idea = Reverb(i)
                x = self.add_idea(idea)
                x = self.go_to_the_source(x)
                return [x]

        idea = Noun.from_features(features)
        x = self.add_idea(idea)
        return [x]

    def resolve_each_noun(self, features):
        true_ii = set()
        for i in range(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_noun_features(
                    features, self.ideas, self.place_kinds):
                true_i = self.go_to_the_source(i)
                if true_i in true_ii:
                    continue
                true_ii.add(true_i)
                n = self.ideas[true_i]
                yield n

    def resolve_plural_noun(self, features):
        rr = []
        for i in range(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_noun_features(
                    features, self.ideas, self.place_kinds):
                idea = Reverb(i)
                x = self.add_idea(idea)
                x = self.go_to_the_source(x)
                rr.append(x)
                if 1 < len(rr):
                    return rr

        idea = Noun.from_feature(features)
        x = self.add_idea(idea)
        return [x]

    def resolve_one_clause(self, features):
        for i in range(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if not idea:
                continue
            if idea.matches_clause_features(features, self.ideas):
                return i

        return None

    def decode_adjective(self, deep_ref, from_xx, to_xx):
        adj = deep_ref.arg.s
        noun = Noun(attributes=[adj])
        x = self.add_idea(noun)
        return [[x]]

    def decode_conjunction(self, deep_ref, from_xx, to_xx):
        xxx = []
        for a in deep_ref.arg.aa:
            sub_deep_ref = DeepReference(
                owning_clause_id=deep_ref.owning_clause_id,
                is_subj=deep_ref.is_subj, arg=a)
            sub_xxx = self.decode(sub_deep_ref, from_xx, to_xx)
            if len(sub_xxx) != 1:
                return None
            xxx.append(sub_xxx[0])

        op = deep_ref.arg.op
        if op == Conjunction.ALL_OF:
            xx = reduce(lambda a, b: a + b, xxx)
            xx = sorted(set(xx))
            return [xx]
        elif op == Conjunction.ONE_OF:
            return xxx
        else:
            assert False

    def decode_common_noun(self, deep_ref, from_xx, to_xx):
        n = deep_ref.arg

        assert not n.possessor

        if n.number and n.number.is_interrogative() and not n.rels_nargs:
            assert n.selector.correlative == Correlative.INDEF
            idea = Noun(query=Query.CARDINALITY, attributes=n.attributes,
                        kind=n.noun)
            x = self.add_idea(idea)
            return [[x]]

        if n.selector.correlative == Correlative.INDEF and not n.rels_nargs:
            if n.selector.n_min == N5.SING and n.selector.n_max == N5.SING:
                # Create a new one.
                idea = Noun(attributes=n.attributes, kind=n.noun)
                x = self.add_idea(idea)
                return [[x]]
            elif N5.DUAL <= n.selector.n_min:
                # It's referring to all of instances with those fields.
                features = NounFeatures(
                    query=Query.GENERIC, attributes=n.attributes, kind=n.noun)
                xx = self.resolve_one_noun(features)
                return [xx]
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
            return [[x]]

        d = n.selector.dump()
        del d['correlative']
        if d != {
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        }:
            pass  # TODO: actually handle this correctly.

        rel2xxx = {}
        for rel, narg in n.rels_nargs:
            sub_ref = DeepReference(
                owning_clause_id=deep_ref.owning_clause_id, is_subj=False,
                arg=narg)
            xxx = self.decode(sub_ref, from_xx, to_xx)
            rel2xxx[rel] = xxx

        if n.noun == 'person':
            gender = None
        else:
            gender = Gender.NEUTER
        features = NounFeatures(
            attributes=n.attributes, kind=n.noun, gender=gender,
            rel2xxx=rel2xxx)
        xx = self.resolve_one_noun(features)
        return [xx]

    def decode_comparative(self, deep_ref, from_xx, to_xx):
        sub_deep_ref = DeepReference(
            owning_clause_id=deep_ref.owning_clause_id, is_subj=False,
            arg=deep_ref.arg.than)
        sub_xxx = self.decode(sub_deep_ref, from_xx, to_xx)
        xxx = []
        for sub_xx in sub_xxx:
            xx = []
            for sub_x in sub_xx:
                comp = Comparative(
                    deep_ref.arg.polarity, deep_ref.arg.adjective, sub_x)
                x = self.add_idea(comp)
                xx.append(x)
            xxx.append(xx)
        return xxx

    def decode_content_clause(self, deep_ref, from_xx, to_xx):
        c = deep_ref.arg

        # We use the clause ID to tell decode reflexives and so on recursively.
        clause_id = self.new_clause_id()

        # Translate each verb argument to a disjunction of conjunctions of
        # memory indexes.
        rel2xxx = {}
        for i, (rel, varg) in enumerate(c.rels_vargs):
            is_subj = i == c.subj_index
            deep_ref = DeepReference(clause_id, is_subj, varg)
            xxx = self.decode(deep_ref, from_xx, to_xx)
            if xxx is None:
                return None

            # Learn "places".
            if rel in self.place_rels:
                for xx in xxx:
                    for x in xx:
                        idea = self.ideas[x]
                        if isinstance(idea, Noun):
                            if not idea.kind:
                                continue
                            self.place_kinds.add(idea.kind)

            assert xxx
            rel2xxx[rel] = xxx

        # The rest are unchanged in the conversion to memory.
        idea = Clause(c.status, c.purpose, c.is_intense, c.verb, c.adverbs,
                      rel2xxx)

        x = self.add_idea(idea)
        xx = [x]
        return [xx]

    def decode_direction(self, deep_ref, from_xx, to_xx):
        sub_deep_ref = DeepReference(
            owning_clause_id=deep_ref.owning_clause_id, is_subj=False,
            arg=deep_ref.arg.of)
        sub_xxx = self.decode(sub_deep_ref, from_xx, to_xx)
        xxx = []
        for sub_xx in sub_xxx:
            xx = []
            for sub_x in sub_xx:
                dr = Direction(deep_ref.arg.which, sub_x)
                x = self.add_idea(dr)
                xx.append(x)
            xxx.append(xx)
        return xxx

    def decode_personal_pronoun(self, deep_ref, from_xx, to_xx):
        d = deep_ref.arg.declension

        if d == Declension.WHO1:
            who = Noun.make_who()
            x = self.add_idea(who)
            return [[x]]
        elif d == Declension.WHO2:
            who = Noun.make_who()
            x = self.add_idea(who)
            return [[x]]
        elif d == Declension.YOU:
            return [to_xx]
        elif d == Declension.HE:
            features = NounFeatures(gender=Gender.MALE, kind='person')
        elif d == Declension.SHE:
            features = NounFeatures(gender=Gender.FEMALE, kind='person')
        elif d == Declension.THEY2:
            features = NounFeatures(kind='person')
            xx = self.resolve_plural_noun(features)
            return [xx]
        else:
            print('Unhandled declension, bailing on this dsen:', \
                Declension.to_str[d])
            return None

        xx = self.resolve_one_noun(features)
        return [xx]

    def decode_proper_noun(self, deep_ref, from_xx, to_xx):
        name = deep_ref.arg.name
        name = tuple([s.title() for s in name])
        gender = self.gender_clf.classify(name)
        features = NounFeatures(name=name, gender=gender)
        xx = self.resolve_one_noun(features)
        return [xx]

    def decode_time_of_day(self, deep_ref, from_xx, to_xx):
        t = deep_ref.arg
        n = RelativeDay(t.day_offset, t.section)
        x = self.add_idea(n)
        xx = [x]
        return [xx]

    def decode(self, deep_ref, from_xx, to_xx):
        """
        (DeepReference, from_xx, to_xx) -> disjunction of conjunctions of index
        """
        f = self.type2decode[type(deep_ref.arg)]
        return f(deep_ref, from_xx, to_xx)

    def decode_dsen(self, dsen, from_xx, to_xx):
        deep_ref = DeepReference(
            owning_clause_id=None, is_subj=False, arg=dsen.root)
        xxx = self.decode(deep_ref, from_xx, to_xx)
        if xxx is None:
            return None

        assert len(xxx) == 1
        xx, = xxx
        assert len(xx) == 1
        x, = xx
        return x
