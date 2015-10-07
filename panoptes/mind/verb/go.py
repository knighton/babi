from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import Query, RelativeDay
from panoptes.mind.know.location import At
from panoptes.mind.verb.base import ClauseMeaning, Response


GO_LEMMAS = ['go', 'journey', 'move', 'travel']


def go_common(c, memory, agent_xx, to_xx, when_xx=None):
    if len(to_xx) != 1:
        return None

    if when_xx and len(when_xx) != 1:
        return None

    if when_xx:
        when_x, = when_xx
        when = memory.ideas[when_x]
        if isinstance(when, RelativeDay):
            time_span = when.to_time_span()
        else:
            time_span = None
    else:
        time_span = None

    to_x, = to_xx
    for x in agent_xx:
        agent = memory.ideas[x]
        loc = At(to_x)
        agent.location_history.set_location(loc, time_span)
        for x2 in agent.carrying:
            loc = At(to_x)
            memory.ideas[x2].location_history.set_location(loc, time_span)

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
        return go_common(c, memory, agent_xx, to_xx, when_xx)


class HowGoFromToQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = GO_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.FROM_SOURCE, Relation.TO_LOCATION,
             Relation.WAY],
        ]

    def handle(self, c, memory, (agent_xx, source_xx, to_xx, how_xx)):
        if len(source_xx) != 1:
            return None

        if len(to_xx) != 1:
            return None

        if len(how_xx) != 1:
            return None

        how = memory.ideas[how_xx[0]]
        if how.query != Query.IDENTITY:
            return None

        for x in agent_xx:
            agent = memory.ideas[x]
            if agent.query:
                return None

        source_x, = source_xx
        source = memory.ideas[source_x]
        if source.query:
            return None

        to_x, = to_xx
        to = memory.ideas[to_x]
        if to.query:
            return None

        ss = memory.graph.decide_path(source_x, to_x)
        ss = map(lambda s: s[0], ss)
        s = ','.join(ss)
        return Response(s)
