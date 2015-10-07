from panoptes.ling.morph.comparative.comparative import ComparativePolarity
from panoptes.mind.idea.base import Idea


class Comparative(Idea):
    def __init__(self, polarity, adjective, than_x):
        self.polarity = polarity
        self.adjective = adjective
        self.than_x = than_x

    def dump(self):
        return {
            'type': 'Comparative',
            'polarity': ComparativePolarity.to_str[self.polarity],
            'adjective': self.adjective,
            'than_x': self.than_x,
        }
