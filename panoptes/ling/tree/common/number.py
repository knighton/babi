from panoptes.ling.glue.inflection import Conjugation


def tokens_from_int(n):
    return {
        0: 'zero',
        1: 'one',
        2: 'two',
        3: 'three',
        4: 'four',
        5: 'five',
    }[n]


class Number(object):
    """
    Simple hack because I don't want the full thing yet.
    """

    def __init__(self, n):
        self.n = n
        if self.n is not None:
            assert isinstance(self.n, int)

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        return {
            'type': 'Number',
            'n': self.n,
        }

    def is_interrogative(self):
        return self.n is None

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        if self.n is None:
            tokens = ['how', 'many']
        else:
            tokens = tokens_from_int(self.n)
        return SayResult(tokens=tokens, conjugation=Conjugation.S3,
                         eat_prep=False)

    @staticmethod
    def load(d, loader):
        return Number(d['n'])
