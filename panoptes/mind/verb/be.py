from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import Identity
from panoptes.mind.verb.base import ClauseMeaning, Response


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


class AgentIn(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['be']
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
            agent.location = -1
            return Response()
        else:
            return None


class AgentInQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = ['be']
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
        if agent.location is None:
            return Response('dunno')
        elif agent.location == place_x:
            return Response('yes')
        else:
            return Response('no')
