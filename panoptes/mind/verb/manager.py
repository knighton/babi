from collections import defaultdict

from panoptes.mind.verb.be import AgentPlaceQuestion, AgentInQuestion
from panoptes.mind.verb.carry import Bring, Drop, Go, PickUp, \
    CarryingWhatQuestion
from panoptes.mind.verb.give import Give, GiveQuestion


class VerbSemanticsManager(object):
    def __init__(self, memory):
        self.memory = memory

        self.vv = [
            AgentPlaceQuestion(),
            AgentInQuestion(),

            Bring(),
            Drop(),
            Go(),
            PickUp(),
            CarryingWhatQuestion(),

            Give(),
            GiveQuestion(),
        ]

        self.purpose_lemma2xx = defaultdict(list)
        for i, v in enumerate(self.vv):
            for lemma in v.lemmas:
                self.purpose_lemma2xx[(v.purpose, lemma)].append(i)

    def handle(self, c):
        xx = self.purpose_lemma2xx[(c.purpose, c.verb.lemma)]
        if not xx:
            return None

        for x in xx:
            v = self.vv[x]
            for rels in v.signatures:
                xxx = []
                ok = True
                for rel in rels:
                    if rel is None:
                        xxx.append(None)
                        continue

                    xx = c.rel2xx.get(rel)
                    if xx is None:
                        ok = False
                        break

                    xxx.append(xx)
                if not ok:
                    continue

                r = v.handle(c, self.memory, xxx)
                if r:
                    return r

        return None
