from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.verb.base import ClauseMeaning, Response


class FitsInside(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['fit']
        self.signatures = [
            [Relation.AGENT, Relation.INSIDE],
        ]

    def handle(self, c, memory, (agent_xx, inside_xx)):
        if len(agent_xx) != 1:
            return None

        if len(inside_xx) != 1:
            return None

        agent_x, = agent_xx
        inside_x, = inside_xx
        memory.graph.link(agent_x, 'smaller', inside_x)

        return Response()
