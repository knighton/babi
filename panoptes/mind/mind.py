import json
from random import randint

from panoptes.ling.glue.inflection import Declension
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.tree.common.util.selector import Correlative
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.deep.common_noun import DeepCommonNoun
from panoptes.ling.tree.deep.content_clause import DeepContentClause
from panoptes.mind.idea import Clause, Identity, Noun, View, idea_from_view
from panoptes.mind.semantics import SemanticsManager


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


class OverhearResult(object):
    def __init__(self, out=None):
        self.out = out


class Mind(object):
    def __init__(self):
        self.ideas = []
        self.uid2x = {}
        self.type2decode = {
            ProperNoun: self.decode_proper_noun,
            DeepCommonNoun: self.decode_common_noun,
            DeepContentClause: self.decode_content_clause,
        }
        self.next_clause_id = 0

        self.place_rels = set([
            Relation.PLACE,
            Relation.TO_LOCATION,
        ])

        self.place_kinds = set()

        self.semantics_mgr = SemanticsManager()

    def show(self):
        print '-' * 80
        print 'Mind:'
        for i, idea in enumerate(self.ideas):
            print '[%d]' % i
            print json.dumps(idea.dump(), indent=4, sort_keys=True)
        print '-' * 80

    def new_clause_id(self):
        r = self.next_clause_id
        self.next_clause_id += 1
        return r

    def new_user(self):
        uid = randint(0, 0x7FFFFFFFFFFFFFFF)
        assert uid not in self.uid2x
        x = len(self.ideas)
        self.ideas.append(Noun(kind='person'))
        self.uid2x[uid] = x
        return uid

    def add_idea(self, idea):
        x = len(self.ideas)
        self.ideas.append(idea)
        return x

    def resolve_one(self, view):
        for i in xrange(len(self.ideas) - 1, -1, -1):
            idea = self.ideas[i]
            if idea.matches(view, self.place_kinds):
                return [i]

        idea = idea_from_view(view)
        x = self.add_idea(idea)
        return [x]

    def decode_proper_noun(self, deep_ref, from_xx, to_xx):
        view = View(name=deep_ref.arg.name)
        return self.resolve_one(view)

    def decode_common_noun(self, deep_ref, from_xx, to_xx):
        n = deep_ref.arg
        assert not n.possessor
        assert n.selector.correlative in [
            Correlative.DEF,
            Correlative.DIST,
            Correlative.INTR
        ]
        d = n.selector.dump()
        del d['correlative']
        assert d == {
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        }
        assert not n.number
        assert not n.attributes
        assert not n.rels_nargs

        if n.selector.correlative == Correlative.INTR:
            idea = Noun(identity=Identity.REQUESTED, selector=n.selector,
                        kind=n.noun)
            x = self.add_idea(idea)
            return [x]

        view = View(kind=n.noun)
        return self.resolve_one(view)

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
            rel2xx[rel] = xx

        # The rest are unchanged in the conversion to memory.
        idea = Clause(c.status, c.purpose, c.is_intense, c.verb, rel2xx)

        x = self.add_idea(idea)
        return [x]

    def decode(self, deep_ref, from_xx, to_xx):
        """
        (DeepReference, from_xx, to_xx) -> xx
        """
        f = self.type2decode[type(deep_ref.arg)]
        return f(deep_ref, from_xx, to_xx)

    def learn_places(self, c):
        for rel in self.place_rels:
            if rel not in c.rel2xx:
                continue
            for x in c.rel2xx[rel]:
                idea = self.ideas[x]
                kind = idea.kind
                if not kind:
                    continue
                self.place_kinds.add(kind)

    def overhear(self, dsen, from_uids, to_uids):
        cutoff = len(self.ideas)

        from_xx = map(lambda u: self.uid2x[u], from_uids)
        to_xx = map(lambda u: self.uid2x[u], to_uids)
        deep_ref = DeepReference(
            owning_clause_id=None, is_subj=False, arg=dsen.root)
        x, = self.decode(deep_ref, from_xx, to_xx)
        c = self.ideas[x]

        r = self.semantics_mgr.handle(c, self.ideas)
        if r:
            self.learn_places(c)
        else:
            self.ideas = self.ideas[:cutoff]
        print type(r)
        return r
