from collections import defaultdict

from panoptes.mind.verb.be import AgentIsTarget, AgentTargetQuestion, \
    AgentPlaceBeforeQuestion, AgentPlaceQuestion, AgentIn, AgentInQuestion
from panoptes.mind.verb.carry import Bring, CarryingWhatQuestion, Drop, GoTo, \
    GoToAfter, GoToAt, PickUp
from panoptes.mind.verb.give import Give, GiveQuestion


class VerbSemanticsManager(object):
    def __init__(self, memory):
        self.memory = memory

        self.vv = [
            AgentIsTarget(),
            AgentTargetQuestion(),
            AgentPlaceBeforeQuestion(),
            AgentPlaceQuestion(),
            AgentIn(),
            AgentInQuestion(),

            Bring(),
            Drop(),
            GoTo(),
            GoToAfter(),
            GoToAt(),
            PickUp(),
            CarryingWhatQuestion(),

            Give(),
            GiveQuestion(),
        ]

        self.purpose_lemma2xx = defaultdict(list)
        for i, v in enumerate(self.vv):
            for lemma in v.lemmas:
                self.purpose_lemma2xx[(v.purpose, lemma)].append(i)

    def try_meaning(self, meaning, c):
        for rels in meaning.signatures:
            # Relations must match.
            if sorted(filter(bool, rels)) != sorted(c.rel2xx):
                continue

            # Collect args of each relation, in signature order.
            xxx = []
            for rel_or_none in rels:
                if rel_or_none is None:
                    xxx.append(None)
                    continue

                xx = c.rel2xx[rel_or_none]
                xxx.append(xx)

            # Try to execute it.
            r = meaning.handle(c, self.memory, xxx)
            if r:
                return r

        return None

    def handle(self, c):
        xx = self.purpose_lemma2xx[(c.purpose, c.verb.lemma)]
        for x in xx:
            meaning = self.vv[x]
            r = self.try_meaning(meaning, c)
            if r:
                return r

        return None
