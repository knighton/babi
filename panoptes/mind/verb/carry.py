from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import Identity
from panoptes.mind.verb.base import ClauseMeaning, Response


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
        self.lemmas = ['discard', 'drop', 'leave', 'put']
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
