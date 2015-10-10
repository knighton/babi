from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.verb.verb import Tense
from panoptes.mind.idea.noun import Noun, Query
from panoptes.mind.idea.time import RelativeDay
from panoptes.mind.know.cause_effect import CAUSE2EFFECTS, GO2CAUSE
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


class GoWhereQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = GO_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.PLACE],
        ]

    def handle(self, c, memory, (agent_xx, to_xx)):
        if len(agent_xx) != 1:
            return None

        if len(to_xx) != 1:
            return None

        agent_x, = agent_xx
        to_x, = to_xx
        agent = memory.ideas[agent_x]
        to = memory.ideas[to_x]
        if isinstance(agent, Noun) and isinstance(to, Noun):
            if not agent.query and to.query == Query.IDENTITY and \
                    to.kind == 'place':
                if c.verb.tense == Tense.FUTURE:
                    for adj in agent.attributes:
                        effects = CAUSE2EFFECTS.get(adj)
                        if not effects:
                            continue
                        for verb, target in effects:
                            if verb == 'go':
                                return Response(target)
                    return Response('dunno')
                else:
                    return None
            else:
                return None
        else:
            return None


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

        ss = memory.graph.shortest_path(to_x, source_x)
        ss = map(lambda s: s.split('_')[1][0], ss)
        ss.reverse()
        s = ','.join(ss)
        return Response(s)


class WhyGoToQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = GO_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TO, Relation.REASON],
            [Relation.AGENT, Relation.TO, Relation.BECAUSE],
        ]

    def handle(self, c, memory, (agent_xx, to_xx, why_xx)):
        if len(agent_xx) != 1:
            return None

        if len(to_xx) != 1:
            return None

        if len(why_xx) != 1:
            return None

        agent_x, = agent_xx
        to_x, = to_xx
        why_x, = why_xx
        agent = memory.ideas[agent_x]
        to = memory.ideas[to_x]
        why = memory.ideas[why_x]
        if isinstance(agent, Noun) and isinstance(to, Noun) and \
                isinstance(why, Noun):
            if not agent.query and not to.query and why.query == Query.IDENTITY:
                cause = GO2CAUSE.get(to.kind, 'dunno')
                return Response(cause)
            else:
                return None
        else:
            return None
