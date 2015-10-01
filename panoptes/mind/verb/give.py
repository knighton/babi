from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.glue.relation import Relation
from panoptes.mind.idea import ClauseView, Identity
from panoptes.mind.verb.base import ClauseMeaning, Response


class Give(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.INFO
        self.lemmas = ['give', 'hand', 'pass']
        self.signatures = [
            [Relation.AGENT, Relation.TO_RECIPIENT, Relation.TARGET],
        ]

    def handle(self, c, memory, (give_xx, recv_xx, what_xx)):
        if len(give_xx) != 1:
            return None

        if len(recv_xx) != 1:
            return None

        return Response()


class GiveQuestion(ClauseMeaning):
    def __init__(self):
        self.purpose = Purpose.WH_Q
        self.lemmas = ['give', 'hand']
        self.signatures = [
            [Relation.AGENT, Relation.TO_RECIPIENT,  Relation.TARGET],
        ]

    def handle(self, c, memory, (give_xx, recv_xx, what_xx)):
        if len(give_xx) != 1:
            return None

        if len(recv_xx) != 1:
            return None

        if len(what_xx) != 1:
            return None

        giver = memory.ideas[give_xx[0]]
        receiver = memory.ideas[recv_xx[0]]
        what = memory.ideas[what_xx[0]]

        q_count = \
            (giver.identity == Identity.REQUESTED) + \
            (receiver.identity == Identity.REQUESTED) + \
            (what.identity == Identity.REQUESTED)

        if q_count != 1:
            return None

        if giver.identity == Identity.REQUESTED:
            rel2xx = {
                Relation.TO_RECIPIENT: recv_xx,
                Relation.TARGET: what_xx,
            }
            want_rel = Relation.AGENT
        elif receiver.identity == Identity.REQUESTED:
            rel2xx = {
                Relation.AGENT: give_xx,
                Relation.TARGET: what_xx,
            }
            want_rel = Relation.TO_RECIPIENT
        elif what.identity == Identity.REQUESTED:
            rel2xx = {
                Relation.AGENT: give_xx,
                Relation.TO_RECIPIENT: recv_xx,
            }
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
            return Response('wtf')
