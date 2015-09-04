from copy import deepcopy

from base.combinatorics import each_choose_one_from_each
from ling.glue.inflection import Conjugation
from ling.glue.purpose import EndPunctClassifier
from ling.parse.parse import Parse
from ling.surface.clause import Clause
from ling.surface.proper_noun import ProperNoun
from ling.surface.sentence import Sentence


class VerbExtractor(object):
    """
    Finds and parses verbs.
    """

    def __init__(self, verb_mgr):
        self.verb_mgr = verb_mgr

    def extract_all(self, root_token):
        """
        subtree -> yields (verb span pair, SurfaceVerbs)

        Find and parse all possible verbs at the root of the given parse
        subtree.
        """
        # Find all words that make up the verb.
        tt = [root_token]
        for rel, t in root_token.downs:
            if rel == 'aux':
                tt.append(t)

        # Put them in order.
        tt.sort(key=lambda t: t.index)

        # Group consecutive tokens into contiguous spans of verb words.
        spans = []
        begin = 0
        end = begin
        word_tuples = []
        word_tuple = []
        for token in tt[1:]:
            x = token.index

            # If we're part of the same span, just grow it by one.
            #
            # If we're separate, start a new span.
            if end + 1 == x:
                end = x
                word_tuple.append(token.text)
            else:
                spans.append((begin, end))
                begin = x
                end = x
                word_tuples.append(word_tuple)
                word_tuple = [token.text]
        spans.append((begin, end))
        word_tuples.append(word_tuple)

        # Parse given spans.
        if len(spans) == 1:
            # Try the verb words as "pre" words.  Eg, "Did she?"
            sss = tuple(word_tuples[0]), ()
            vv = self.verb_mgr.parse(sss)
            if vv:
                yield (spans[0], None), vv

            # Try the verb words as "main" words.  Eg, "She did."
            sss = (), tuple(word_tuples[0])
            vv = self.verb_mgr.parse(sss)
            if vv:
                yield (None, spans[0]), vv
        elif len(spans) == 2:
            # Both spans present.  Eg, "Did she know?"
            sss = tuple(word_tuples)
            vv = self.verb_mgr.parse(sss)
            if vv:
                yield tuple(spans), vv
        else:
            # Should never happen.  That would be an interesting parse indeed.
            # Some kind of parser failure.
            assert False

    def extract(self, root_token, is_root_clause):
        """
        subtree, whether root clause -> yields (verb span pair, SurfaceVerbs)

        Find and parse all possible verbs at the root of the given parse
        subtree, then rule out invalid ones.
        """
        for verb_span_pair, vv in self.extract_all(root_token):
            vv = filter(lambda v: v.can_be_in_root_clause(), vv)
            if vv:
                yield verb_span_pair, vv


class SurfaceRecognizer(object):
    def __init__(self, verb_mgr):
        self.end_punct_clf = EndPunctClassifier()
        self.verb_extractor = VerbExtractor(verb_mgr)

        self.tag2recognize = {
            'NNP': self.recognize_nnp,
        }

    def recognize_nnp(self, root_token):
        return [ProperNoun(root_token.text)]

    def recognize_verb_arg(self, root_token):
        return self.tag2recognize[root_token.tag](root_token)

    def find_subject(self, verb_span_pair, token_indexes):
        a, b = verb_span_pair
        if a and b:
            # Both spans ("would you see?"): find the argument that goes between
            # the spans.
            for i, x in enumerate(token_indexes):
                if a[1] < x < b[0]:
                    return i
        elif a:
            # Just the pre span ("would you?"): find the argument directly
            # after the verb words.
            for i, x in enumerate(token_indexes):
                if a[1] < x:
                    return i
        elif b:
            # Just the main span ("you would", "go!"): find the argument
            # preceding the one directly after the verb words, or return None if
            # there isn't one (in the case of imperatives).
            for i, x in enumerate(token_indexes):
                if b[1] < x:
                    if 0 <= i - 1:
                        return i - 1
                    else:
                        return None
        else:
            assert False

    def extract_verb_args(self, root_token, verb_span_pair):
        """
        root token, verb span pair -> subj arg index, options per arg

        ... where an option is a (prep, verb arg).
        """
        token_indexes = []
        ppp_nnn = []
        for rel, t in root_token.downs:
            if rel not in ('nsubj', 'dobj'):
                continue
            token_indexes.append(t.index)
            pp = [()]
            nn = self.recognize_verb_arg(t)
            pp_nn = []
            for p, n in each_choose_one_from_each([pp, nn]):
                pp_nn.append((p, n))
            ppp_nnn.append(pp_nn)
        subj_argx = self.find_subject(verb_span_pair, token_indexes)
        return subj_argx, ppp_nnn

    def conjs_from_verb(self, v):
        """
        recognized verb with wildcards -> possible conjugations
        """
        # If the verb's field is a wildcard, it could be any of them.
        if v.conj == None:
            v_conjs = Conjugation.values
        else:
            v_conjs = set([v.conj])

        # If imperative, it just be conjugated second person.
        if v.intrinsics.modality.flavor == ModalFlavor.IMPERATIVE:
            v_conjs &= (Conjugation.S2, Conjugation.P2)

        return v_conjs

    def conjs_from_verb_args(self, pp_nn, subj_argx):
        """
        verb arguments -> possible conjugations
        """
        # It's possible to have no subject, in the case of imperatives.  In that
        # case, choose second person.
        if subj_argx is None:
            return set([Conjugation.S2, Conjugation.P2])

        # Get the required conjugation from the subject.
        conj = pp_nn[subj_x][1].conjugation()

        # In case of existential there, get conjugation from the object instead.
        if not conj:
            x = subj_argx + 1
            if not (0 <= x < len(pp_nn)):
                return []  # Ex-there but no object = can't parse it.
            conj = pp_nn[x][1].conjugation()

        return set([conj])

    def possible_conjugations(self, v, pp_nn, subj_argx):
        """
        verb and arguments -> possible conjugations

        Verb agreement.
        """
        v_conjs = self.conjs_from_verb(v)
        n_conjs = self.conjs_from_verb_args(pp_nn, subj_argx)
        return v_conjs & n_conjs

    def recognize_clause(self, root_token, is_root_clause):
        """
        root token -> yields Clause
        """
        cc = []
        for verb_span_pair, vv in \
                self.verb_extractor.extract(root_token, is_root_clause):
            subj_argx, ppp_nnn = self.extract_verb_args(
                root_token, verb_span_pair)
            for v in vv:
                for pp_nn in each_choose_one_from_each(ppp_nnn):
                    for conj in self.possible_conjugations(v, pp_nn, subj_argx):
                        ctzr = Complementizer.ZERO
                        new_v = deepcopy(v)
                        new_v.conj = conj
                        is_pos = False
                        c = Clause(ctzr, new_v, deepcopy(pp_nn), subj_argx,
                                   is_pos)
                        cc.append(c)
        return cc

    def recog(self, parse):
        """
        Parse -> yields Sentence
        """
        assert isinstance(parse, Parse)

        assert parse.tokens
        end_punct = self.end_punct_clf.classify(parse.tokens[-1])

        for clause in self.recognize_clause(parse.root, is_root_clause):
            yield Sentence(clause, end_punct)
