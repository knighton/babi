from copy import deepcopy

from panoptes.ling.glue.inflection import Declension
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.tree.common.util.selector import Correlative
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.deep.common_noun import DeepCommonNoun
from panoptes.ling.tree.deep.content_clause import DeepContentClause
from panoptes.ling.tree.deep.direction import DeepDirection
from panoptes.mind.idea import Clause, Identity, Noun, View, idea_from_view


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
            ProperNoun: self.decode_proper_noun,
            DeepCommonNoun: self.decode_common_noun,
            DeepContentClause: self.decode_content_clause,
            DeepDirection: self.decode_direction,
        }

        self.next_clause_id = 0

        self.place_rels = set([
            Relation.PLACE,
            Relation.TO_LOCATION,
        ])

        self.place_kinds = set()

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

    def show(self):
        print '=' * 80
        print 'Memory'
        print '-' * 80
        for i, idea in enumerate(self.ideas):
            print '\t\t[%d]' % i
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
        if d != {
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        }:
            return []

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

            # Learn "places".
            if rel in self.place_rels:
                for x in xx:
                    idea = self.ideas[x]
                    if not idea.kind:
                        continue
                    self.place_kinds.add(idea.kind)

            rel2xx[rel] = xx

        # The rest are unchanged in the conversion to memory.
        idea = Clause(c.status, c.purpose, c.is_intense, c.verb, rel2xx)

        x = self.add_idea(idea)
        return [x]

    def decode_direction(self, deep_ref, from_xx, to_xx):
        return []

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
