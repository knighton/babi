from panoptes.ling.glue.inflection import InflectionManager
from panoptes.ling.glue.purpose import PurposeManager
from panoptes.ling.glue.relation import RelationManager
from panoptes.ling.morph.plural import PluralManager
from panoptes.ling.parse.parser import Parser as TextToParse
from panoptes.ling.tree.deep.base import DeepState
from panoptes.ling.tree.common.personal_pronoun import PersonalManager
from panoptes.ling.tree.surface.base import SayContext, SayState
from panoptes.ling.tree.surface.recog import ParseToSurface
from panoptes.ling.tree.surface.util.correlative import CorrelativeManager
from panoptes.ling.tree.surface.util.count_restriction import \
    CountRestrictionChecker
from panoptes.ling.tree.surface.util.shortcut import ShortcutManager
from panoptes.ling.verb.verb_manager import VerbManager


class SurfaceToDeep(object):
    pass


class English(object):
    def __init__(self):
        conj_f = 'panoptes/config/conjugations.csv'
        verb_f = 'data/verbs.json'
        verb_mgr = VerbManager.from_files(conj_f, verb_f)

        count_restriction_mgr = CountRestrictionChecker()
        correlative_mgr = CorrelativeManager(count_restriction_mgr)
        shortcut_mgr = ShortcutManager(count_restriction_mgr)

        inflection_mgr = InflectionManager()
        personal_mgr = PersonalManager(inflection_mgr)

        cat_f = 'panoptes/config/plural/categories.yaml'
        rule_f = 'panoptes/config/plural/rules.txt'
        nonsuffixable_f = 'panoptes/config/plural/nonsuffixable.txt'
        cap_f = 'panoptes/config/plural/capitalized.txt'
        plural_mgr = PluralManager.from_files(
            cat_f, rule_f, nonsuffixable_f, cap_f)

        say_state = SayState(
            correlative_mgr, inflection_mgr, personal_mgr, plural_mgr,
            shortcut_mgr)

        # The SayContext is needed for conjugation.  None of its fields affect
        # conjugation for any object.
        arbitrary_say_context = SayContext(
            prep=None, has_left=False, has_right=False, is_possessive=False)
        purpose_mgr = PurposeManager()
        relation_mgr = RelationManager()
        deep_state = DeepState(arbitrary_say_context, purpose_mgr, relation_mgr)

        # Text -> surface structure -> deep structure.
        self.text_to_parse = TextToParse()
        self.parse_to_surface = ParseToSurface(
            correlative_mgr, personal_mgr, plural_mgr, say_state, verb_mgr)
        self.surface_to_deep = SurfaceToDeep()

    def each_dsen_from_text(self, text):
        print '--Agent.put--'
        for parse in self.text_to_parse.parse(text):
            print '>', parse.dump()
            for surf in self.parse_to_surface.recog(parse):
                print '>>', surf
        if False:
            yield 7  # TODO: hack to yield nothing until this is implemented.

    def text_from_dsen(self, dsen):
        ssen = dsen.to_surface(self.deep_state, self.surface_state, idiolect)
        return ssen.say(self.surface_state, idiolect)
