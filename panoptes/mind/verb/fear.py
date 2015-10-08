from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea.clause import ClauseFeatures
from panoptes.mind.idea.noun import Noun, NounFeatures, Query
from panoptes.mind.verb.base import ClauseMeaning, Response


# Due to a parser hack to make "afraid of" a passive verb for sanity's sake (and
# there are etymological justifications too, you know).
#
# thwack(agent, target) means "the agent causes the target to fear the agent".
BEFEAR_LEMMAS = ['thwack']


FEAR_LEMMAS = ['fear']


class Befear(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = BEFEAR_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET]
        ]

    def handle(self, c, memory, (agent_xx, target_xx)):
        if len(agent_xx) != 1:
            return None

        if len(target_xx) != 1:
            return None

        return Response()


class Fear(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = FEAR_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET]
        ]

    def handle(self, c, memory, (agent_xx, target_xx)):
        if len(agent_xx) != 1:
            return None

        if len(target_xx) != 1:
            return None

        return Response()


class BefearQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = BEFEAR_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (agent_xx, target_xx)):
        if len(agent_xx) != 1:
            return None

        agent_x, = agent_xx
        agent = memory.ideas[agent_x]

        if len(target_xx) != 1:
            return None

        target_x, = target_xx
        target = memory.ideas[target_x]

        if isinstance(agent, Noun) and isinstance(target, Noun):
            if agent.query == Query.IDENTITY and not target.query:
                rel2xx = {
                    Relation.TARGET: target_xx,
                }
                features = ClauseFeatures(
                    possible_lemmas=BEFEAR_LEMMAS, rel2xx=rel2xx)
                c = memory.resolve_one_clause(features)
                if c is None:
                    if not target.kind:
                        return Response('dunno')

                    features = NounFeatures(
                        query=Query.GENERIC, kind=target.kind)
                    target_kind_xx = memory.resolve_one_noun(features)
                    if len(target_kind_xx) != 1:
                        return Response('todo')

                    rel2xx = {
                        Relation.TARGET: target_kind_xx,
                    }
                    features = ClauseFeatures(
                        possible_lemmas=BEFEAR_LEMMAS, rel2xx=rel2xx)
                    c = memory.resolve_one_clause(features)

                if c is None:
                    return Response('dunno')

                c = memory.ideas[c]
                got_xxx = c.rel2xxx.get(Relation.AGENT)
                if not got_xxx:
                    return Reponse('dunno')

                if len(got_xxx) != 1:
                    return Response('todo')
                got_xx, = got_xxx

                rr = []
                for x in got_xx:
                    n = memory.ideas[x]
                    if not isinstance(n, Noun):
                        rr.append('not_a_noun')
                    elif n.name:
                        rr.append(' '.join(n.name))
                    elif n.kind:
                        rr.append(n.kind)
                    else:
                        assert False
                return Response(','.join(rr))
            else:
                return None
        else:
            return None
