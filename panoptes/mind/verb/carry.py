from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import Identity
from panoptes.mind.location import At
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
        if len(agent_xx) != 1:
            return None

        if len(to_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]
        to_x, = to_xx
        for x in target_xx:
            agent.carrying.append(x)
            target = memory.ideas[x]
            loc = At(to_x)
            target.location_history.update_location(loc)

        return Response()


class Drop(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['discard', 'drop', 'leave', 'put']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
            [Relation.AGENT, Relation.TARGET, Relation.TO_LOCATION],
            [Relation.AGENT, Relation.TARGET, None],
        ]

    def handle(self, c, memory, (agent_xx, target_xx, to_xx)):
        if to_xx and len(to_xx) != 1:
            return None

        for x in agent_xx:
            agent = memory.ideas[x]
            agent.carrying = filter(
                lambda n: n not in target_xx, agent.carrying)

        if to_xx:
            to_x, = to_xx
            for x in target_xx:
                target = memory.ideas[x]
                loc = At(to_x)
                target.location_history.update_location(loc)

        return Response()


class Go(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['go', 'journey', 'move', 'travel']
        self.signatures = [
            [Relation.AGENT, Relation.PLACE,       Relation.AFTER],
            [Relation.AGENT, Relation.PLACE,       None],
            [Relation.AGENT, Relation.TO_LOCATION, Relation.AFTER],
            [Relation.AGENT, Relation.TO_LOCATION, None],
        ]

    def handle(self, c, memory, (agent_xx, to_xx, after_xx)):
        if len(to_xx) != 1:
            return None

        to_x, = to_xx
        for x in agent_xx:
            agent = memory.ideas[x]
            loc = At(to_x)
            agent.location_history.update_location(loc)
            for x2 in agent.carrying:
                loc = At(to_x)
                memory.ideas[x2].location_history.update_location(loc)

        return Response()


class PickUp(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['get', 'grab', 'pick']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
            [Relation.AGENT, Relation.TARGET, None],
        ]

    def handle(self, c, memory, (agent_xx, target_xx, at_xx)):
        if len(agent_xx) != 1:
            return None

        if at_xx and len(at_xx) != 1:
            return None

        if at_xx:
            at_x, = at_xx
        else:
            at_x = None
        x, = agent_xx
        agent = memory.ideas[x]
        for x in target_xx:
            agent.carrying.append(x)
            if at_x is not None:
                loc = At(at_x)
                memory.ideas[x].location_history.update_location(loc)

        return Response()


class CarryingWhatQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = ['carry']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (agent_xx, what_xx)):
        if len(agent_xx) != 1:
            return None

        if len(what_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]
        what = memory.ideas[what_xx[0]]

        if agent.identity == Identity.REQUESTED:
            return None
        elif what.identity == Identity.REQUESTED:
            pass
        else:
            assert False

        rr = []
        for x in agent.carrying:
            n = memory.ideas[x]
            rr.append(n.kind)

        if rr:
            s = ','.join(rr)
            return Response(s)
        else:
            return Response('nothing')
