from random import randint

from panoptes.ling.glue.inflection import Declension
from panoptes.ling.tree.common.util.selector import Correlative
from panoptes.mind.idea import Clause, Noun, View, idea_from_view


ACTIVATION_DECAY = 0.6
assert 0.0 < ACTIVATION_DECAY < 1.0


ACTIVATION_CUTOFF = 0.5
assert 0.0 < ACTIVATION_CUTOFF < 1.0


class Mind(object):
    def __init__(self):
        self.ideas = []
        self.uid2x = {}

    def new_user(self):
        uid = randint(0, 0x7FFFFFFFFFFFFFFF)
        assert uid not in self.uid2x
        x = len(self.ideas)
        self.ideas.append(Noun(noun='person'))
        self.uid2x[uid] = x
        return uid

    def add_idea(self, idea):
        x = len(self.ideas)
        self.ideas.append(idea)
        return x

    def add_idea_from_view(self, view):
        idea = idea_from_view(view)
        return self.add_idea(idea)

    def resolve_one(self, view):
        scores_xx = []
        for i in xrange(len(self.ideas) - 1, 0, -1):
            idea = self.ideas[i]
            percent = idea.relevance(view)
            score = percent * bump
            bump *= ACTIVATION_DECAY * (1 - percent)
            scores_xx.append((score, x))

        sum_of_scores = sum(map(lambda (f, x): f, scores_xx))
        if sum_of_scores != 0.0:
            scores_xx = map(lambda (f, x): f / sum_of_scores, scores_xx)

        xxx = []
        scores_xx.sort(reverse=True)
        for score, x in scores_xx:
            if score < ACTIVATION_CUTOFF:
                break
            xx = [x]
            xxx.append(xx)

        if not xxx:
            x = self.add_idea_from_view(view)
            xx = [x]
            xxx.append(xx)

        return xxx

    def decode_proper_noun(self, deep_ref, from_xx, to_xx):
        view = View(name=deep_ref.name)
        return self.resolve_one(view)

    def decode_common_noun(self, deep_ref, from_xx, to_xx):
        n = deep_ref.arg
        assert not n.possessor
        assert n.selector.correlative in (Correlative.DEF, Correlative.DIST)
        d = n.selector.dump()
        del d['correlative']
        assert d == {
            'correlative': 'DEF',
            'n_min': 'SING',
            'n_max': 'SING',
            'of_n_min': 'SING',
            'of_n_max': 'SING',
        }
        assert not n.number
        assert not n.attributes
        assert not n.rels_nargs

        view = View(noun=n.noun)
        return self.resolve_one(view)

    def overhear(self, dsen, from_uids, to_uids):
        pass

