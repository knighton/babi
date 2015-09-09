from ling.glue.inflection import InflectionManager
from ling.morph.plural import PluralManager
from ling.parse.parser import Parser as TextToParse
from ling.tree.common.base import SayState
from ling.tree.common.personal_pronoun import PersonalManager
from ling.tree.surface.recog import ParseToSurface
from ling.tree.surface.util.correlative import CorrelativeManager
from ling.tree.surface.util.count_restriction import CountRestrictionChecker
from ling.verb.verb_manager import VerbManager


class SurfaceToDeep(object):
    pass


class DeepToSurface(object):
    pass


class SurfaceToText(object):
    pass


class English(object):
    def __init__(self):
        conj_f = 'config/conjugations.csv'
        verb_f = '../data/verbs.json'
        verb_mgr = VerbManager.from_files(conj_f, verb_f)

        count_restriction_checker = CountRestrictionChecker()
        correlative_mgr = CorrelativeManager(count_restriction_checker)

        inflection_mgr = InflectionManager()
        personal_mgr = PersonalManager(inflection_mgr)

        cat_f = 'config/plural/categories.yaml'
        rule_f = 'config/plural/rules.txt'
        nonsuffixable_f = 'config/plural/nonsuffixable.txt'
        cap_f = 'config/plural/capitalized.txt'
        plural_mgr = PluralManager.from_files(
            cat_f, rule_f, nonsuffixable_f, cap_f)

        say_state = SayState(
            correlative_mgr, inflection_mgr, personal_mgr, plural_mgr)

        # Text -> deep structure.
        self.text_to_parse = TextToParse()
        self.parse_to_surface = ParseToSurface(say_state, verb_mgr)
        self.surface_to_deep = SurfaceToDeep()

        # Deep structure -> text.
        self.deep_to_surface = DeepToSurface()
        self.surface_to_text = SurfaceToText()

    def each_dsen_from_text(self, text):
        print '--Agent.put--'
        for parse in self.text_to_parse.parse(text):
            print '>', parse.dump()
            for surf in self.parse_to_surface.recog(parse):
                print '>>', surf
        if False:
            yield 7  # TODO: hack to yield nothing until this is implemented.

    def text_from_dsen(self, dsen):
        assert False  # XXX
