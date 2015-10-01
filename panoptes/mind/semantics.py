from collections import defaultdict

from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import Identity


class Response(object):
    def __init__(self, text=None):
        self.text = text


class ClauseMeaning(object):
    """
    Implements a clause.
    """

    def handle(self, c, memory, xxx):
        """
        (Clause, list of Ideas, idea indexes per arg) -> Response or None
        """
        raise NotImplementedError


class Go(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['go', 'journey', 'move', 'travel']
        self.signatures = [
            [Relation.AGENT, Relation.PLACE],
            [Relation.AGENT, Relation.TO_LOCATION],
        ]

    def handle(self, c, memory, (agent_xx, to_xx)):
        if len(to_xx) != 1:
            return None

        to_x, = to_xx
        for x in agent_xx:
            agent = memory.ideas[x]
            agent.location = to_x
            for x2 in agent.carrying:
                memory.ideas[x2].location = to_x

        return Response()


class PickUp(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['get', 'grab', 'pick']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, None],
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
        ]

    def handle(self, c, memory, (agent_xx, target_xx, at_xx)):
        if len(agent_xx) != 1:
            return None

        x, = agent_xx
        agent = memory.ideas[x]
        for x in target_xx:
            agent.carrying.append(x)

        return Response()


class Bring(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['take']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
            [Relation.AGENT, Relation.TARGET, Relation.TO_LOCATION],
        ]

    def handle(self, c, memory, (agent_xx, target_xx, to_xx)):
        if len(to_xx) != 1:
            return None

        to_x, = to_xx
        for x in target_xx:
            target = memory.ideas[x]
            target.location = to_x

        return Response()


class Drop(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['drop', 'put']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
            [Relation.AGENT, Relation.TARGET, Relation.TO_LOCATION],
        ]

    def handle(self, c, memory, (agent_xx, target_xx, to_xx)):
        if len(to_xx) != 1:
            return None

        to_x, = to_xx
        for x in target_xx:
            target = memory.ideas[x]
            target.location = to_x

        return Response()


class Give(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['give', 'hand']
        self.signatures = [
            [Relation.AGENT, Relation.TO_RECIPIENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (give_xx, recv_xx, what_xx)):
        if len(give_xx) != 1:
            return None

        if len(recv_xx) != 1:
            return None

        return Response()


class AgentPlaceQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = ['be']
        self.signatures = [
            [Relation.AGENT, Relation.PLACE],
        ]

    def handle(self, c, memory, (agent_xx, loc_xx)):
        if len(agent_xx) != 1:
            return None

        if len(loc_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]
        place = memory.ideas[loc_xx[0]]

        if agent.identity == Identity.REQUESTED:
            return None
        elif place.identity == Identity.REQUESTED:
            x = agent.location
            if x is None:
                return Response('dunno')
            loc = memory.ideas[x]
            return Response(loc.kind)
        else:
            assert False


class GiveQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = ['give', 'hand']
        self.signatures = [
            [Relation.AGENT, Relation.TO_RECIPIENT,  Relation.TARGET],
        ]

    def handle(self, c, memory, (give_xx, recv_xx, what_xx)):
        if len(give_xx) != 1:
            return None

        if len(recv_xx) != 1:
            return None

        if len(what_xx) != 1:
            return None

        giver = memory.ideas[give_xx[0]]
        receiver = memory.ideas[recv_xx[0]]
        what = memory.ideas[what_xx[0]]

        q_count = \
            giver.identity == Identity.REQUESTED + \
            receiver.identity == Identity.REQUESTED + \
            what.identity == Identity.REQUESTED

        if q_count != 1:
            return None

        if giver.identity == Identity.REQUESTED:
            rel2xx = {
                Relation.TO_RECIPIENT: recv_xx,
                Relation.TARGET: what_xx,
            }
            want_rel = Relation.AGENT
        elif receiver.identity == Identity.REQUESTED:
            rel2xx = {
                Relation.AGENT: give_xx,
                Relation.TARGET: what_xx,
            }
            want_rel = Relation.TO_RECIPIENT
        elif what.identity == Identity.REQUSTED:
            rel2xx = {
                Relation.AGENT: give_xx,
                Relation.TO_RECIPIENT: recv_xx,
            }
            want_rel = Relation.TARGET
        else:
            assert False

        # TODO


class SemanticsManager(object):
    def __init__(self, memory):
        self.memory = memory

        self.vv = [
            Go(),
            PickUp(),
            Bring(),
            Drop(),
            Give(),
            AgentPlaceQuestion(),
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
