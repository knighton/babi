class Direction(Idea):
    def __init__(self, which, of_x):
        self.which = which
        self.of_x = of_x

    def dump(self):
        return {
            'type': 'Direction',
            'which': self.which,
            'of_x': self.of_x,
        }
