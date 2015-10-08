from collections import defaultdict

from panoptes.mind.verb.be import *
from panoptes.mind.verb.carry import *
from panoptes.mind.verb.fear import *
from panoptes.mind.verb.fit import *
from panoptes.mind.verb.go import *
from panoptes.mind.verb.give import *


class VerbSemanticsManager(object):
    def __init__(self, memory):
        self.memory = memory

        self.vv = [
            AgentIsTarget(),
            AgentIsTargetQuestion(),
            AgentTargetQuestion(),
            AgentIsTo(),
            IsAgentToQuestion(),
            AgentIsAbove(),
            AgentIsBelow(),
            IsAgentAbove(),
            IsAgentBelow(),
            AgentPlaceBeforeQuestion(),
            AgentPlaceQuestion(),
            AgentIn(),
            AgentInQuestion(),

            Take(),
            Drop(),
            PickUp(),
            CarryingWhatQuestion(),

            Befear(),
            Fear(),
            BefearQuestion(),

            FitsInside(),
            DoesItFitInside(),

            GoTo(),
            GoToAfter(),
            GoToAt(),
            HowGoFromToQuestion(),

            Give(),
            GiveQuestion(),
            ReceiveQuestion(),
        ]

        self.purpose_lemma2xx = defaultdict(list)
        for i, v in enumerate(self.vv):
            for lemma in v.lemmas:
                self.purpose_lemma2xx[(v.purpose, lemma)].append(i)

    def try_meaning(self, meaning, c):
        for rels in meaning.signatures:
            # Relations must match.
            if sorted(filter(bool, rels)) != sorted(c.rel2xxx):
                continue

            # Collect args of each relation (disjunctions of conjunctions), in
            # signature order.
            xxxx = []
            for rel_or_none in rels:
                if rel_or_none is None:
                    xxxx.append(None)
                    continue

                xxx = c.rel2xxx[rel_or_none]
                xxxx.append(xxx)

            # Try to re-collect the args as just conjunctions.
            xxx = []
            ok = True
            for arg_xxx in xxxx:
                if arg_xxx is None:
                    xxx.append(None)
                elif len(arg_xxx) == 1:
                    xx, = arg_xxx
                    xxx.append(xx)
                else:
                    ok = False
                    break

            # Handle the args.
            if ok:
                r = meaning.handle(c, self.memory, xxx)
                if r:
                    return r
            else:
                if hasattr(meaning, 'handle_disjunctions'):
                    r = meaning.handle_disjunctions(c, self.memory, xxxx)
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
