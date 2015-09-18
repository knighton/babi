from panoptes.ling.verb.conjugation import Conjugator
from panoptes.ling.verb.verb_parser import VerbParser
from panoptes.ling.verb.verb_sayer import VerbSayer
from panoptes.ling.verb.verb import SurfaceVerb


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
    def from_files(conjugation_f, verb_f):
        conjugator = Conjugator.from_file(conjugation_f)
        sayer = VerbSayer(conjugator)
        parser = VerbParser.load_or_regenerate(sayer, verb_f)
        return VerbManager(sayer, parser)

    def say(self, v):
        """
        SurfaceVerb -> (string tuple, string tuple)
        """
        assert isinstance(v, SurfaceVerb)
        return self.sayer.say(v)

    def get_all_say_options(self, v):
        """
        SurfaceVerb -> list of (string tuple, string tuple)
        """
        assert isinstance(v, SurfaceVerb)
        for sss in self.sayer.get_all_say_options(v):
            yield sss

    def parse(self, sss):
        """
        (string tuple, string tuple) -> list of SurfaceVerb
        """
        return self.parser.parse(sss)
