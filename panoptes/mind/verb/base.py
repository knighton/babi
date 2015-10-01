class Response(object):
    def __init__(self, text=None):
        self.text = text


class ClauseMeaning(object):
    """
    Implements a clause.
    """

    def handle(self, c, memory, xxx):
        """
        (Clause, list of Ideas, idea indexes per arg) -> Response or None
        """
        raise NotImplementedError
