from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import ClauseView, Query
from panoptes.mind.verb.base import ClauseMeaning, Response


GIVE_LEMMAS = ['give', 'hand', 'pass']


class Give(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = GIVE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TO_RECIPIENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (give_xx, recv_xx, what_xx)):
        if len(recv_xx) != 1:
            return None

        for give_x in give_xx:
            giver = memory.ideas[give_x]
            giver.carrying = filter(lambda x: x not in what_xx, giver.carrying)

        for recv_x in recv_xx:
            receiver = memory.ideas[recv_x]
            receiver.carrying += what_xx

            xx = []
            seen = set()
            for x in receiver.carrying:
                if x in seen:
                    continue
                xx.append(x)
            receiver.carrying = xx

        return Response()


class GiveQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = GIVE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TO_RECIPIENT, Relation.TARGET],
            [Relation.AGENT, None,                  Relation.TARGET],
        ]

    def handle(self, c, memory, (give_xx, recv_xx, what_xx)):
        if len(give_xx) != 1:
            return None

        if recv_xx and len(recv_xx) != 1:
            return None

        if len(what_xx) != 1:
            return None

        giver = memory.ideas[give_xx[0]]
        receiver = memory.ideas[recv_xx[0]] if recv_xx else None
        what = memory.ideas[what_xx[0]]

        q_count = int(bool(giver.query))
        if receiver:
            q_count += bool(receiver.query)
        q_count += bool(what.query)

        if q_count != 1:
            return None

        if giver.query == Query.IDENTITY:
            rel2xx = {
                Relation.TARGET: what_xx,
            }
            if receiver:
                rel2xx[Relation.TO_RECIPIENT] = recv_xx
            want_rel = Relation.AGENT
        elif receiver and receiver.query == Query.IDENTITY:
            rel2xx = {
                Relation.AGENT: give_xx,
                Relation.TARGET: what_xx,
            }
            want_rel = Relation.TO_RECIPIENT
        elif what.query == Query.IDENTITY:
            rel2xx = {
                Relation.AGENT: give_xx,
            }
            if receiver:
                rel2xx[Relation.TO_RECIPIENT] = recv_xx
            want_rel = Relation.TARGET
        else:
            assert False

        view = ClauseView(possible_lemmas=self.lemmas, rel2xx=rel2xx)
        x = memory.resolve_one_clause(view)
        if x is None:
            return Response('dunno')

        c = memory.ideas[x]
        xx = c.rel2xx[want_rel]
        if len(xx) != 1:
            return None

        x, = xx
        n = memory.ideas[x]
        if n.name:
            return Response(' '.join(n.name))
        elif n.kind:
            return Response(n.kind)
        else:
            return Response('cat got my tongue')


RECEIVE_LEMMAS = ['receive']


class ReceiveQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = RECEIVE_LEMMAS
        self.signatures = [
            [Relation.AGENT, Relation.TARGET, Relation.FROM_SOURCE],
            [Relation.AGENT, Relation.TARGET, None],
        ]

    def handle(self, c, memory, (recv_xx, what_xx, source_xx)):
        if len(recv_xx) != 1:
            return None

        if source_xx and len(source_xx) != 1:
            return None

        receiver = memory.ideas[recv_xx[0]]
        what = memory.ideas[what_xx[0]]
        source = memory.ideas[source_xx[0]] if source_xx else None

        q_count = 0
        if receiver.query:
            q_count += 1
        if what.query:
            q_count += 1
        if source and source.query:
            q_count += 1

        if q_count != 1:
            return None

        # give_agent_xx = source_xx
        # give_target_xx = what_xx
        # give_to_recip_xx = recv_xx
        if receiver.query == Query.IDENTITY:
            give_rel2xx = {
                Relation.TARGET: target_xx,
            }
            if source:
                give_rel2xx[Relation.AGENT] = source_xx
            give_want_rel = Relation.TO_RECIPIENT
        elif what.query == Query.IDENTITY:
            give_rel2xx = {
                Relation.TO_RECIPIENT: recv_xx,
            }
            if source:
                give_rel2xx[Relation.AGENT] = source_xx
            give_want_rel = Relation.TARGET
        elif source and source.query == Query.IDENTITY:
            give_rel2xx = {
                Relation.TARGET: what_xx,
                Relation.TO_RECIPIENT: recv_xx,
            }
            give_want_rel = Relation.AGENT
        else:
            assert False

        view = ClauseView(possible_lemmas=GIVE_LEMMAS, rel2xx=give_rel2xx)
        x = memory.resolve_one_clause(view)
        if x is None:
            return Response('dunno')

        c = memory.ideas[x]
        xx = c.rel2xx[give_want_rel]
        if len(xx) != 1:
            return None

        x, = xx
        n = memory.ideas[x]
        if n.name:
            return Respnose(' '.join(n.name))
        elif n.kind:
            return Response(n.kind)
        else:
            return Response('cat got my tongue')
