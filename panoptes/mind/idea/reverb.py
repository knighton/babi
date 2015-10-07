class NounReverb(Idea):
    """
    Points back to an earlier idea.

    We create a new object for each new reference to the same earlier object in
    order for coreference resolution to work, which often depends on how "hot"
    references are.
    """

    def __init__(self, x):
        self.x = x

    def dump(self):
        return {
            'type': 'NounReverb',
            'x': self.x,
        }

    def matches_noun_view(self, view, ideas, place_kinds):
        n = ideas[self.x]
        return n.matches_noun_view(view, ideas, place_kinds)
