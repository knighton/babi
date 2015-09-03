from ling.verb.conjugation import Conjugator
from ling.verb.verb_parser import VerbParser
from ling.verb.verb_sayer import VerbSayer
from ling.verb.verb import SurfaceVerb


class VerbManager(object):
    """
    Handles everything about verbs.
    """

    def __init__(self, sayer, parser):
        self.sayer = sayer
        assert isinstance(self.sayer, VerbSayer)

        self.parser = parser
        assert isinstance(self.parser, VerbParser)

    @staticmethod
    def load_or_regenerate(conjugation_f, verb_f):
        conjugator = Conjugator.from_file(conjugation_f)
        sayer = VerbSayer(conjugator)
        parser = VerbParser.load_or_regenerate(sayer, verb_f)
        return VerbManager(sayer, parser)

    def say(self, v):
        assert isinstance(v, SurfaceVerb)
        return self.sayer.say(v)

    def get_all_say_options(self, v):
        assert isinstance(v, SurfaceVerb)
        for sss in self.sayer.get_all_say_options(v):
            yield sss

    def parse(self, sss):
        return self.parser.parse(sss)
