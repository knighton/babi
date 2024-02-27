from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.verb.base import ClauseMeaning, Response


class FitsInside(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['fit']
        self.signatures = [
            [Relation.AGENT, Relation.INSIDE],
            [Relation.AGENT, Relation.IN],
        ]

    def handle(self, c, memory, xxx_todo_changeme):
        (agent_xx, inside_xx) = xxx_todo_changeme
        if len(agent_xx) != 1:
            return None

        if len(inside_xx) != 1:
            return None

        agent_x, = agent_xx
        inside_x, = inside_xx
        memory.graph.link(agent_x, 'is_smaller_than', inside_x)

        return Response()


class DoesItFitInside(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.TF_Q
        self.lemmas = ['fit']
        self.signatures = [
            [Relation.AGENT, Relation.INSIDE],
            [Relation.AGENT, Relation.IN],
        ]

    def handle(self, c, memory, xxx_todo_changeme1):
        (agent_xx, inside_xx) = xxx_todo_changeme1
        if len(agent_xx) != 1:
            return None

        if len(inside_xx) != 1:
            return None

        agent_x, = agent_xx
        inside_x, = inside_xx
        s = memory.graph.is_direction(agent_x, 'is_smaller_than', inside_x)
        return Response(s)
