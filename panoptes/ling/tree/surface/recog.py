from copy import deepcopy

from panoptes.etc.combinatorics import each_choose_one_from_each
from panoptes.ling.glue.grammatical_number import N2, N3, N5, \
    nx_eq_nx_is_possible, nx_to_nxs
from panoptes.ling.glue.idiolect import Idiolect
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.glue.magic_token import A_OR_AN
from panoptes.ling.glue.purpose import EndPunctClassifier
from panoptes.ling.parse.parse import Parse
from panoptes.ling.tree.common.existential_there import ExistentialThere
from panoptes.ling.tree.common.personal_pronoun import PersonalPronoun, \
    PersonalPronounCase
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.surface.base import SayContext, SayState
from panoptes.ling.tree.surface.common_noun import SurfaceCommonNoun
from panoptes.ling.tree.surface.content_clause import Complementizer, \
    SurfaceContentClause
from panoptes.ling.tree.surface.sentence import SurfaceSentence
from panoptes.ling.verb.annotation import annotate_as_aux
from panoptes.ling.verb.verb import ModalFlavor


class VerbExtractor(object):
    """
    Finds and parses verbs.
    """

    def __init__(self, verb_mgr):
        self.verb_mgr = verb_mgr

    def maybe_annotate_as_aux(self, s):
        if s in ['have', 'has', 'had']:
            return annotate_as_aux(s)
        else:
            return s

    def extract_all(self, root_token):
        """
        subtree -> yields (verb span pair, SurfaceVerbs)

        Find and parse all possible verbs at the root of the given parse
        subtree.
        """
        # Find all words that make up the verb.
        tt = [root_token]
        for rel, t in root_token.downs:
            if rel in ['neg']:
                tt.append(t)
            elif rel in ['aux', 'auxpass']:
                t.text = self.maybe_annotate_as_aux(t.text)
                tt.append(t)

        # Put them in order.
        tt.sort(key=lambda t: t.index)

        # Group consecutive tokens into contiguous spans of verb words.
        spans = []
        begin = tt[0].index
        end = begin
        word_tuples = []
        word_tuple = [tt[0].text]
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
                word_tuples.append(tuple(word_tuple))
                word_tuple = [token.text]
        spans.append((begin, end))
        word_tuples.append(tuple(word_tuple))

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


class ParseToSurface(object):
    """
    Object that converts parses to surface structure.
    """

    def __init__(self, det_pronoun_mgr, personal_mgr, plural_mgr, say_state,
                 verb_mgr):
        # For extracting the correct verb conjugation from subjects.
        self.arbitrary_idiolect = Idiolect()
        self.say_state = say_state
        self.subject_say_context = SayContext(
            prep=None, has_left=True, has_right=True, is_possessive=False)

        self.end_punct_clf = EndPunctClassifier()
        self.verb_extractor = VerbExtractor(verb_mgr)

        self.det_pronoun_mgr = det_pronoun_mgr
        self.personal_mgr = personal_mgr
        self.plural_mgr = plural_mgr

        self.tag2recognize = {
            'DT': self.recog_dt,
            'EX': self.recog_ex,
            'NN': self.recog_nn,
            'NNS': self.recog_nns,
            'NNP': self.recog_nnp,
            'PRP': self.recog_prp,
            'WP': self.recog_wp,
        }

    def recog_dt(self, root_token):
        rr = []
        for selector in self.det_pronoun_mgr.parse_pronoun(root_token.text):
            r = SurfaceCommonNoun(selector=selector)
            rr.append(r)
        return rr

    def recog_ex(self, root_token):
        return [ExistentialThere()]

    def recog_dt_nn(self, root_token, noun, gram_n2):
        if not len(root_token.downs) == 1:
            return []

        dep, child = root_token.downs[0]
        if dep != 'det':
            return []

        s = child.text

        if s in ['a', 'an']:
            s = A_OR_AN

        rr = []
        for selector in self.det_pronoun_mgr.parse_determiner(s):
            for selector in selector.restricted_to_grammatical_number(
                    gram_n2, self.det_pronoun_mgr.cor2res_gno):
                r = SurfaceCommonNoun(selector=selector, noun=noun)
                rr.append(r)
        return rr

    def recog_posdet_nn(self, root_token, noun, gram_n2):
        """
        * PRP$ NN(S)
        * WP$ NN(S)
        """
        if not len(root_token.downs) == 1:
            return []

        dep, child = root_token.downs[0]
        if dep != 'poss':
            return []

        rr = []
        for declension in self.personal_mgr.posdet_parse((child.text,)):
            pos = PersonalPronoun(declension, PersonalPronounCase.OBJECT)

            correlative = Correlative.DEF
            count_restriction = self.det_pronoun_mgr.cor2res_gno[correlative][0]
            selector = Selector.from_correlative(correlative, count_restriction)
            if not selector:
                continue
            for selector in selector.restricted_to_grammatical_number(
                    gram_n2, self.det_pronoun_mgr.cor2res_gno):
                r = SurfaceCommonNoun(possessor=pos, selector=selector,
                                      noun=noun)
                rr.append(r)
        return rr

    def recog_common_noun(self, root_token, noun, n2):
        rr = self.recog_dt_nn(root_token, noun, n2)
        rr += self.recog_posdet_nn(root_token, noun, n2)
        return rr

    def recog_nn(self, root_token):
        sing = root_token.text
        return self.recog_common_noun(root_token, sing, N2.SING)

    def recog_nns(self, root_token):
        rr = []
        for sing in self.plural_mgr.to_singular(root_token.text):
            for r in self.recog_common_noun(root_token, sing, N2.PLUR):
                rr.append(r)
        return rr

    def recog_nnp(self, root_token):
        name = root_token.text,
        return [ProperNoun(name=name, is_plur=False)]

    def recog_prp(self, root_token):
        ss = root_token.text,
        return self.personal_mgr.perspro_parse(ss)

    def recog_wp(self, root_token):
        rr = []

        # For WP like "what".
        for selector in self.det_pronoun_mgr.parse_pronoun(root_token.text):
            r = SurfaceCommonNoun(selector=selector)
            rr.append(r)

        # For WP like "who".
        ss = root_token.text,
        rr += self.personal_mgr.perspro_parse(ss)

        return rr

    def recognize_verb_arg(self, root_token):
        return self.tag2recognize[root_token.tag](root_token)

    def find_subject(self, verb_span_pair, varg_root_indexes):
        """
        args -> subj arg index, vmain index
        """
        a, b = verb_span_pair
        if a and b:
            # Both spans ("would you see?"): find the argument that goes between
            # the spans.
            for i, arg in enumerate(varg_root_indexes):
                if a[1] < arg < b[0]:
                    return i, i + 1

            assert False
        elif a:
            # We must have args.
            assert varg_root_indexes

            # Just the pre span ("would you?"): find the argument directly
            # after the verb words.
            for i, arg in enumerate(varg_root_indexes):
                if a[1] < arg:
                    return i, i + 1
        elif b:
            # Just the main span ("you would", "go!").

            # If no args, we're done.
            if not varg_root_indexes:
                return None, 0

            # Find the argument preceding the one directly after the verb words,
            # or subject index = None if no subject (imperative).
            for i, arg in enumerate(varg_root_indexes):
                if b[1] < arg:
                    if 0 <= i - 1:
                        return i - 1, i
                    else:
                        return None, i

            # Didn't find any argument after the verb, so the last one is the
            # subject.  TODO: "because of that, go!" -> because is not
            # imperative subject.
            n = len(varg_root_indexes) - 1
            return n, n + 1
        else:
            assert False

    def extract_verb_args(self, root_token, verb_span_pair):
        """
        root token, verb span pair -> subj arg index, vmain idx, options per arg

        ... where an option is a (prep, verb arg).
        """
        varg_root_indexes = []
        ppp_nnn = []
        for rel, t in root_token.downs:
            if rel not in ('nsubj', 'nsubjpass', 'agent', 'dobj', 'dative',
                           'expl', 'attr'):
                continue

            if rel == 'agent':
                assert len(t.downs) == 1
                rel, down = t.downs[0]
                assert rel == 'pobj'
                t = down

            varg_root_indexes.append(t.index)
            pp = [None]
            nn = self.recognize_verb_arg(t)
            pp_nn = []
            for p, n in each_choose_one_from_each([pp, nn]):
                pp_nn.append((p, n))
            ppp_nnn.append(pp_nn)

        subj_argx, vmain_index = \
            self.find_subject(verb_span_pair, varg_root_indexes)

        return subj_argx, vmain_index, ppp_nnn

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
            v_conjs &= set([Conjugation.S2, Conjugation.P2])

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
        conj = pp_nn[subj_argx][1].decide_conjugation(
            self.say_state, self.arbitrary_idiolect,
            self.subject_say_context)

        # In case of existential there, get conjugation from the object instead.
        if not conj:
            x = subj_argx + 1
            if not (0 <= x < len(pp_nn)):
                return set([])  # Ex-there but no object = can't parse it.
            conj = pp_nn[x][1].decide_conjugation(
                self.say_state, self.arbitrary_idiolect,
                self.subject_say_context)

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
        root token -> yields SurfaceContentClause
        """
        cc = []
        for verb_span_pair, vv in \
                self.verb_extractor.extract(root_token, is_root_clause):
            # Hack to compensate for a bug in imperative verb saying.
            if verb_span_pair[0] and not verb_span_pair[1]:
                vv = filter(lambda v: not v.is_imperative(), vv)
            if not vv:
                continue

            subj_argx, vmain_index, ppp_nnn = self.extract_verb_args(
                root_token, verb_span_pair)

            if subj_argx is None:
                vv = filter(lambda v: v.is_imperative(), vv)
            else:
                assert 0 <= subj_argx < len(ppp_nnn)

            for v in vv:
                for pp_nn in each_choose_one_from_each(ppp_nnn):
                    for conj in self.possible_conjugations(v, pp_nn, subj_argx):
                        complementizer = Complementizer.ZERO
                        new_v = deepcopy(v)
                        new_v.conj = conj
                        c = SurfaceContentClause(
                            complementizer, new_v, deepcopy(pp_nn), vmain_index)
                        cc.append(c)
        return cc

    def recog(self, parse):
        """
        Parse -> yields SurfaceSentence
        """
        assert isinstance(parse, Parse)

        assert parse.tokens
        end_punct = self.end_punct_clf.classify(parse.tokens[-1].text)

        for clause in self.recognize_clause(parse.root, is_root_clause=True):
            yield SurfaceSentence(clause, end_punct)
