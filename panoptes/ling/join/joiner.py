from panoptes.ling.glue.magic_token import A_OR_AN, POSSESSIVE_MARK
from panoptes.ling.join.a_or_an import AOrAnClassifier
from panoptes.ling.join.apos_or_apos_s import AposOrAposSClassifier
from panoptes.ling.join.contraction import ContractionManager
from panoptes.ling.verb.annotation import remove_verb_annotations


class Joiner(object):
    """
    Converts tokens to text.

    It's not as simple as it sounds, because of token annotations, 'magic'
    tokens, contractions, etc.
    """

    def __init__(self):
        self.a_or_an_clf = AOrAnClassifier()
        self.apos_or_apos_s_clf = AposOrAposSClassifier()
        self.contraction_mgr = ContractionManager()

    def handle_apos_or_apos_s(self, tokens):
        rr = []

        i = 1
        while i < len(tokens):
            prev_token = tokens[i - 1]
            token = tokens[i]
            rr.append(prev_token)
            if token == POSSESSIVE_MARK:
                r = self.apos_or_apos_s.classify(prev_token)
                rr.append(r)
                i += 2
            else:
                i += 1

        if i == len(tokens) and tokens:
            rr.append(tokens[-1])

        return rr

    def handle_a_or_an(self, tokens):
        rr = []

        for i in xrange(len(tokens) - 1):
            token = tokens[i]
            next_token = tokens[i + 1]
            if token == A_OR_AN:
                r = self.a_or_an_clf.classify(next_token)
            else:
                r = token
            rr.append(r)

        if tokens:
            s = tokens[-1]
            if s == A_OR_AN:
                r = 'a'  # Guess.
            else:
                r = s
            rr.append(r)

        return rr

    def is_punct(self, token):
        if '?' in token:
            return True

        if '!' in token:
            return True

        if token in ('.', '...', ','):
            return True

        return False

    def do_join(self, tokens):
        is_puncts = map(self.is_punct, tokens)

        rr = []
        for token, is_punct in zip(tokens, is_puncts):
            if not is_punct:
                rr.append(' ')
            rr.append(token)

        return ''.join(rr)[1:]

    def join(self, tokens, use_contractions):
        tokens = self.contraction_mgr.contract(tokens, use_contractions)
        tokens = map(remove_verb_annotations, tokens)
        tokens = self.handle_apos_or_apos_s(tokens)
        tokens = self.handle_a_or_an(tokens)
        text = self.do_join(tokens)
        return text[0].upper() + text[1:]
