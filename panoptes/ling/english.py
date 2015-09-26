import json

from panoptes.ling.glue.inflection import InflectionManager
from panoptes.ling.glue.purpose import PurposeManager
from panoptes.ling.glue.relation import RelationManager
from panoptes.ling.join.joiner import Joiner
from panoptes.ling.morph.plural import PluralManager
from panoptes.ling.parse.parser import Parser as TextToParse
from panoptes.ling.tree.deep.base import TransformState
from panoptes.ling.tree.deep.recog import SurfaceToDeep
from panoptes.ling.tree.common.personal_pronoun import PersonalManager
from panoptes.ling.tree.surface.base import SayContext, SayState
from panoptes.ling.tree.surface.recog import ParseToSurface
from panoptes.ling.tree.surface.util.pro_adverb import ProAdverbManager
from panoptes.ling.tree.surface.util.pronoun import DetPronounManager
from panoptes.ling.verb.verb_manager import VerbManager


class English(object):
    def __init__(self):
        conj_f = 'panoptes/config/conjugations.csv'
        verb_f = 'data/verbs.json'
        verb_mgr = VerbManager.from_files(conj_f, verb_f)

        det_pronoun_mgr = DetPronounManager()
        pro_adverb_mgr = ProAdverbManager()

        inflection_mgr = InflectionManager()
        personal_mgr = PersonalManager(inflection_mgr)

        cat_f = 'panoptes/config/plural/categories.yaml'
        rule_f = 'panoptes/config/plural/rules.txt'
        nonsuffixable_f = 'panoptes/config/plural/nonsuffixable.txt'
        cap_f = 'panoptes/config/plural/capitalized.txt'
        plural_mgr = PluralManager.from_files(
            cat_f, rule_f, nonsuffixable_f, cap_f)

        self.say_state = SayState(
            det_pronoun_mgr, inflection_mgr, personal_mgr, plural_mgr,
            pro_adverb_mgr, verb_mgr)

        # The SayContext is needed for conjugation.  None of its fields affect
        # conjugation for any object.
        arbitrary_say_context = SayContext(
            prep=None, has_left=False, has_right=False, is_possessive=False)
        purpose_mgr = PurposeManager()
        relation_mgr = RelationManager()
        self.transform_state = \
            TransformState(arbitrary_say_context, purpose_mgr, relation_mgr)

        # Text -> surface structure -> deep structure.
        self.text_to_parse = TextToParse()
        self.parse_to_surface = ParseToSurface(
            det_pronoun_mgr, personal_mgr, plural_mgr, pro_adverb_mgr,
            self.say_state, verb_mgr)
        self.surface_to_deep = SurfaceToDeep(purpose_mgr, relation_mgr)

        self.joiner = Joiner()

    def each_dsen_from_text(self, text, verbose=True):
        parses = []
        for parse in self.text_to_parse.parse(text):
            parse.dump()
            parses.append(parse)

        if verbose:
            print '-- %d parses' % len(parses)

        keys = set()
        keys_ssens = []
        for parse in self.text_to_parse.parse(text):
            for ssen in self.parse_to_surface.recog(parse):
                key = json.dumps(ssen.dump(), indent=4, sort_keys=True)
                if key in keys:
                    continue
                keys_ssens.append((key, ssen))
        keys_ssens.sort()

        if verbose:
            print '-- %d ssens' % len(keys_ssens)

        keys = set()
        keys_dsens = []
        for _ssen in keys_ssens:
            for dsen in self.surface_to_deep.recog(ssen):
                key = json.dumps(ssen.dump(), indent=4, sort_keys=True)
                if key in keys:
                    continue
                keys_dsens.append((key, dsen))
        keys_dsens.sort()

        if verbose:
            print '-- %d dsens' % len(keys_dsens)

        return map(lambda (k, d): d, keys_dsens)

    def text_from_dsen(self, dsen, idiolect):
        ssen = dsen.to_surface(self.transform_state, self.say_state, idiolect)
        tokens = ssen.say(self.say_state, idiolect)
        text = self.joiner.join(tokens, idiolect.contractions)
        return text
