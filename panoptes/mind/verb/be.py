from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.ling.morph.comparative.comparative import ComparativePolarity
from panoptes.mind.idea.comparative import Comparative
from panoptes.mind.idea.direction import Direction
from panoptes.mind.idea.noun import Noun, NounFeatures, Query
from panoptes.mind.know.location import At, NotAt, AtOneOf
from panoptes.mind.verb.base import ClauseMeaning, Response


BE_LEMMAS = ['be']


def get_direction(s):
    return {
        'right': 'is_right_of',
        'left': 'is_left_of',
        'north': 'is_north_of',
        'south': 'is_south_of',
        'east': 'is_east_of',
        'west': 'is_west_of',
    }[s]


class AgentIsTarget(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (agent_xx, target_xx)):
        if len(agent_xx) != 1:
            return None

        if len(target_xx) != 1:
            return None

        agent_x, = agent_xx
        agent = memory.ideas[agent_x]
        target_x, = target_xx
        target = memory.ideas[target_x]
        if isinstance(agent, Noun) and isinstance(target, Comparative):
            if target.polarity == ComparativePolarity.POS and \
                    target.adjective == 'big':
                memory.graph.link(agent_x, 'is_bigger_than', target.than_x)
                return Response()
            else:
                pass
        elif isinstance(agent, Noun) and isinstance(target, Direction):
            direction = get_direction(target.which)
            memory.graph.link(agent_x, direction, target.of_x)
            return Response()
        elif isinstance(agent, Noun) and isinstance(target, Noun):
            agent.assign(target)
            memory.ideas[agent_x] = agent
            memory.ideas[target_x] = None
            return Response()
        else:
            pass

        return None


class AgentIsTargetQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (agent_xx, target_xx)):
        if len(agent_xx) != 1:
            return None

        if len(target_xx) != 1:
            return None

        agent_x, = agent_xx
        target_x, = target_xx

        agent = memory.ideas[agent_x]
        target = memory.ideas[target_x]

        if isinstance(agent, Noun) and isinstance(target, Comparative):
            if target.polarity == ComparativePolarity.POS and \
                    target.adjective == 'big':
                s = memory.graph.is_direction(
                    agent_x, 'is_bigger_than', target.than_x)
                return Response(s)

        return None


COLORS = """
    black
    white
    red
    orange
    yellow
    green
    blue
    violet
""".split()


def is_color(s):
    return s in COLORS


class AgentTargetQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (agent_xx, target_xx)):
        if len(agent_xx) != 1:
            return None

        if len(target_xx) != 1:
            return None

        agent_x, = agent_xx
        agent = memory.ideas[agent_x]
        target_x, = target_xx
        target = memory.ideas[target_x]
        if isinstance(agent, Direction) and isinstance(target, Noun):
            if target.query == Query.IDENTITY:
                direction = get_direction(agent.which)
                xx = memory.graph.look_toward_direction(agent.of_x, direction)
                rr = []
                for x in xx:
                    idea = memory.ideas[x]
                    if idea.name:
                        r = ' '.join(idea.name)
                    elif idea.kind:
                        r = idea.kind
                    else:
                        return None
                    rr.append(r)

                if not rr:
                    return Response('nothing')

                r = ','.join(rr)
                return Response(r)
            else:
                return None
        elif isinstance(agent, Noun) and isinstance(target, Direction):
            of = memory.ideas[target.of_x]
            if of.query == Query.IDENTITY:
                direction = get_direction(target.which)
                xx = memory.graph.look_from_direction(agent_x, direction)
                rr = []
                for x in xx:
                    idea = memory.ideas[x]
                    if idea.name:
                        r = ' '.join(idea.name)
                    elif idea.kind:
                        r = idea.kind
                    else:
                        return None
                    rr.append(r)

                if not rr:
                    return Response('nothing')

                r = ','.join(rr)
                return Response(r)
            else:
                return None
        elif isinstance(agent, Noun) and isinstance(target, Noun):
            if not agent.query and target.query == Query.IDENTITY:
                if target.kind == 'color':
                    for s in agent.attributes:
                        if is_color(s):
                            return Response(s)

                    features = NounFeatures(kind=agent.kind)
                    for n in memory.resolve_each_noun(features):
                        for s in n.attributes:
                            if is_color(s):
                                return Response(s)

                    return Response('dunno')
                else:
                    return None
            else:
                return None
        else:
            return None


def a_direction_b(memory, agent_xx, relation, what_xx):
    agents = map(lambda x: memory.ideas[x], agent_xx)
    for n in agents:
        if not isinstance(n, Noun):
            return None

    whats = map(lambda x: memory.ideas[x], what_xx)
    for n in whats:
        if not isinstance(n, Noun):
            return None

    for agent_x in agent_xx:
        for what_x in what_xx:
            memory.graph.link(agent_x, relation, what_x)

    return Response()


def is_a_direction_b(memory, a_xx, relation, b_xx):
    if len(a_xx) != 1:
        return None

    if len(b_xx) != 1:
        return None

    a_x, = a_xx
    a = memory.ideas[a_x]
    if not isinstance(a, Noun):
        return None

    b_x, = b_xx
    b = memory.ideas[b_x]
    if not isinstance(b, Noun):
        return None

    s = memory.graph.is_direction(a_x, relation, b_x)
    return Response(s)


class AgentIsTo(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TO],
        ]

    def handle(self, c, memory, (agent_xx, to_xx)):
        if len(agent_xx) != 1:
            return None

        if len(to_xx) != 1:
            return None

        agent_x, = agent_xx
        agent = memory.ideas[agent_x]

        to_x, = to_xx
        to = memory.ideas[to_x]

        if isinstance(agent, Noun) and isinstance(to, Direction):
            direction = get_direction(to.which)
            memory.graph.link(agent_x, direction, to.of_x)
            return Response()
        else:
            return None


class IsAgentToQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TO],
        ]

    def handle(self, c, memory, (agent_xx, to_xx)):
        if len(agent_xx) != 1:
            return None

        if len(to_xx) != 1:
            return None

        agent_x, = agent_xx
        agent = memory.ideas[agent_x]

        to_x, = to_xx
        to = memory.ideas[to_x]

        if isinstance(agent, Noun) and isinstance(to, Direction):
            direction = get_direction(to.which)
            return is_a_direction_b(memory, [agent_x], direction, [to.of_x])
        else:
            return None


class AgentIsAbove(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.ABOVE],
        ]

    def handle(self, c, memory, (agent_xx, above_xx)):
        return a_direction_b(memory, agent_xx, 'is_above', above_xx)


class AgentIsBelow(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.BELOW],
        ]

    def handle(self, c, memory, (agent_xx, below_xx)):
        return a_direction_b(memory, agent_xx, 'is_below', below_xx)


class IsAgentAbove(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.ABOVE],
        ]

    def handle(self, c, memory, (agent_xx, above_xx)):
        return is_a_direction_b(memory, agent_xx, 'is_above', above_xx)


class IsAgentBelow(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.BELOW],
        ]

    def handle(self, c, memory, (agent_xx, below_xx)):
        return is_a_direction_b(memory, agent_xx, 'is_below', below_xx)


class AgentPlaceQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = BE_LEMMAS
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

        if agent.query == Query.IDENTITY:
            return None
        elif place.query == Query.IDENTITY:
            x = agent.location_history.get_location()
            if x is None:
                return Response('dunno')
            loc = memory.ideas[x]
            return Response(loc.kind)
        else:
            assert False


class AgentPlaceBeforeQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.PLACE, Relation.BEFORE],
        ]

    def handle(self, c, memory, (what_xx, where_xx, before_xx)):
        if len(what_xx) != 1:
            return None

        if len(where_xx) != 1:
            return None

        if len(before_xx) != 1:
            return None

        what = memory.ideas[what_xx[0]]
        where = memory.ideas[where_xx[0]]
        before_x, = before_xx

        if what.query == Query.IDENTITY:
            return None
        elif where.query == Query.IDENTITY:
            x = what.location_history.get_location_before_location(before_x)
            if x is None:
                return Response('dunno')
            idea = memory.ideas[x]
            return Response(idea.kind)
        else:
            assert False


class AgentIn(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.IN],
        ]

    def handle(self, c, memory, (agent_xx, place_xx)):
        if len(agent_xx) != 1:
            return None

        if len(place_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]
        place_x, = place_xx
        if c.adverbs == ['no', 'longer']:
            loc = NotAt(place_x)
            agent.location_history.set_location(loc)
            return Response()

        if c.verb.polarity.tf:
            loc = At(place_x)
        else:
            loc = NotAt(place_x)
        agent.location_history.set_location(loc)
        return Response()

    def handle_disjunctions(self, c, memory, (agent_xxx, place_xxx)):
        if len(agent_xxx) != 1:
            return None
        agent_xx, = agent_xxx

        for place_xx in place_xxx:
            if len(place_xx) != 1:
                return None
        place_xx = map(lambda xx: xx[0], place_xxx)

        for agent_x in agent_xx:
            agent = memory.ideas[agent_x]
            loc = AtOneOf(place_xx)
            agent.location_history.set_location(loc)

        return Response()


class AgentInQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = BE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.IN],
        ]

    def handle(self, c, memory, (agent_xx, place_xx)):
        if len(agent_xx) != 1:
            return None

        if len(place_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]
        place_x, = place_xx
        r = agent.location_history.is_at_location(place_x)
        if r is None:
            return Response('maybe')
        elif r:
            return Response('yes')
        else:
            return Response('no')
