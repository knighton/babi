import json

from panoptes.ling.glue.inflection import InflectionManager
from panoptes.ling.glue.purpose import PurposeManager
from panoptes.ling.glue.relation import RelationManager
from panoptes.ling.join.joiner import Joiner
from panoptes.ling.morph.plural.plural import PluralManager
from panoptes.ling.parse.parser import Parser as TextToParse
from panoptes.ling.tree.deep.base import TransformState
from panoptes.ling.tree.deep.recog import SurfaceToDeep
from panoptes.ling.tree.common.personal_pronoun import PersonalManager
from panoptes.ling.tree.surface.base import SayContext, SayState
from panoptes.ling.tree.surface.recog import ParseToSurface
from panoptes.ling.tree.surface.util.pro_adverb import ProAdverbManager
from panoptes.ling.tree.surface.util.pronoun import DetPronounManager
from panoptes.ling.verb.verb_manager import VerbManager


class Recognition(object):
    """
    The results of recognizing deep structure in English text.
    """

    def __init__(self, parses, ssens, dsens):
        self.parses = parses
        self.ssens = ssens
        self.dsens = dsens


class English(object):
    def __init__(self):
        conj_f = 'panoptes/config/conjugations.csv'
        verb_f = 'data/verbs.json'
        verb_mgr = VerbManager.from_files(conj_f, verb_f)

        det_pronoun_mgr = DetPronounManager()
        pro_adverb_mgr = ProAdverbManager()

        inflection_mgr = InflectionManager()
        personal_mgr = PersonalManager(inflection_mgr)
        plural_mgr = PluralManager.default()

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

    def recognize(self, text, verbose=True):
        """
        text -> Recognition
        """
        parses = []
        for parse in self.text_to_parse.parse(text):
            parses.append(parse)

        if verbose:
            print '-- %d parses' % len(parses)
            for parse in parses:
                print '-- PARSE'
                parse.dump()

        keys = set()
        keys_ssens = []
        for parse in parses:
            for ssen in self.parse_to_surface.recog(parse):
                key = json.dumps(ssen.dump(), indent=4, sort_keys=True)
                if key in keys:
                    continue
                keys_ssens.append((key, ssen))
        keys_ssens.sort()

        if verbose:
            print '-- %d ssens' % len(keys_ssens)
            for i, (key, ssen) in enumerate(keys_ssens):
                print '-- SSEN %d' % i
                print key

        keys = set()
        keys_dsens = []
        for _, ssen in keys_ssens:
            for dsen in self.surface_to_deep.recog(ssen):
                key = json.dumps(dsen.dump(), indent=4, sort_keys=True)
                if key in keys:
                    continue
                keys_dsens.append((key, dsen))
        keys_dsens.sort()

        if verbose:
            print '-- %d dsens' % len(keys_dsens)
            for i, (key, dsen) in enumerate(keys_dsens):
                print '-- DSEN %d' % i
                print key

        ssens = map(lambda (k, s): s, keys_ssens)
        dsens = map(lambda (k, d): d, keys_dsens)
        return Recognition(parses, ssens, dsens)

    def say(self, dsen, idiolect):
        """
        DeepSentence, Idiolect -> text
        """
        ssen = dsen.to_surface(self.transform_state, self.say_state, idiolect)
        tokens = ssen.say(self.say_state, idiolect)
        text = self.joiner.join(tokens, idiolect.contractions)
        return text
