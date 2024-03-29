from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea.noun import Noun, Query
from panoptes.mind.know.cause_effect import GET2CAUSE
from panoptes.mind.know.location import At
from panoptes.mind.verb.base import ClauseMeaning, Response


class Take(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['take']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
            [Relation.AGENT, Relation.TARGET, Relation.TO_LOCATION],
            [Relation.AGENT, Relation.TARGET, None],
        ]

    def handle(self, c, memory, xxx_todo_changeme):
        (agent_xx, target_xx, to_xx) = xxx_todo_changeme
        if len(agent_xx) != 1:
            return None

        if to_xx and len(to_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]

        for x in target_xx:
            agent.carrying.append(x)

        if to_xx:
            to_x, = to_xx
            for x in target_xx:
                target = memory.ideas[x]
                loc = At(to_x)
                target.location_history.set_location(loc)

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

    def handle(self, c, memory, xxx_todo_changeme1):
        (agent_xx, target_xx, to_xx) = xxx_todo_changeme1
        if to_xx and len(to_xx) != 1:
            return None

        for x in agent_xx:
            agent = memory.ideas[x]
            agent.carrying = [n for n in agent.carrying if n not in target_xx]

        if to_xx:
            to_x, = to_xx
            for x in target_xx:
                target = memory.ideas[x]
                loc = At(to_x)
                target.location_history.set_location(loc)

        return Response()


class PickUp(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['get', 'grab', 'pick']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.PLACE],
            [Relation.AGENT, Relation.TARGET, None],
        ]

    def handle(self, c, memory, xxx_todo_changeme2):
        (agent_xx, target_xx, at_xx) = xxx_todo_changeme2
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
                memory.ideas[x].location_history.set_location(loc)

        return Response()


class WhyPickUp(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = ['get', 'grab', 'pick']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.REASON],
            [Relation.AGENT, Relation.TARGET, Relation.BECAUSE],
        ]

    def handle(self, c, memory, xxx_todo_changeme3):
        (agent_xx, target_xx, why_xx) = xxx_todo_changeme3
        if len(agent_xx) != 1:
            return None

        if len(target_xx) != 1:
            return None

        if len(why_xx) != 1:
            return None

        agent_x, = agent_xx
        target_x, = target_xx
        why_x, = why_xx

        agent = memory.ideas[agent_x]
        target = memory.ideas[target_x]
        why = memory.ideas[why_x]

        if isinstance(agent, Noun) and isinstance(target, Noun) and \
                isinstance(why, Noun):
            if not agent.query and not target.query and \
                    why.query == Query.IDENTITY:
                cause = GET2CAUSE.get(target.kind, 'dunno')
                return Response(cause)
        else:
            return None


def str_from_int(n):
    return {
        0: 'none',
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
    }[n]


class CarryingWhatQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = ['carry']
        self.signatures = [
            [Relation.AGENT, Relation.TARGET],
        ]

    def handle(self, c, memory, xxx_todo_changeme4):
        (agent_xx, what_xx) = xxx_todo_changeme4
        if len(agent_xx) != 1:
            return None

        if len(what_xx) != 1:
            return None

        agent = memory.ideas[agent_xx[0]]
        what = memory.ideas[what_xx[0]]

        if agent.query:
            return None
        elif what.query in (Query.CARDINALITY, Query.IDENTITY):
            pass
        else:
            assert False

        rr = []
        for x in agent.carrying:
            n = memory.ideas[x]
            rr.append(n.kind)

        if what.query == Query.CARDINALITY:
            s = str_from_int(len(rr))
        elif what.query == Query.IDENTITY:
            if rr:
                s = ','.join(rr)
            else:
                s = 'nothing'
        else:
            assert False
        return Response(s)
