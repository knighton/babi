from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.location import At
from panoptes.mind.verb.base import ClauseMeaning, Response


GO_LEMMAS = ['go', 'journey', 'move', 'travel']


def go_common(c, memory, agent_xx, to_xx):
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


class GoTo(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = GO_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.PLACE],
            [Relation.AGENT, Relation.TO_LOCATION],
        ]

    def handle(self, c, memory, (agent_xx, to_xx)):
        return go_common(c, memory, agent_xx, to_xx)


class GoToAfter(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = GO_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.PLACE,       Relation.AFTER],
            [Relation.AGENT, Relation.TO_LOCATION, Relation.AFTER],
        ]

    def handle(self, c, memory, (agent_xx, to_xx, after_xx)):
        return go_common(c, memory, agent_xx, to_xx)


class GoToAt(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = GO_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.PLACE,       Relation.TIME],
            [Relation.AGENT, Relation.TO_LOCATION, Relation.TIME],
        ]

    def handle(self, c, memory, (agent_xx, to_xx, when_xx)):
        return go_common(c, memory, agent_xx, to_xx)
