from copy import deepcopy
from itertools import product

from panoptes.ling.glue.conjunction import STR2CONJUNCTION
from panoptes.ling.glue.grammatical_number import N2, N3, N5, \
    nx_eq_nx_is_possible, nx_to_nxs
from panoptes.ling.glue.idiolect import Idiolect
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.glue.magic_token import A_OR_AN, TIME_PREP
from panoptes.ling.glue.purpose import EndPunctClassifier
from panoptes.ling.parse.parse import Parse
from panoptes.ling.tree.common.adjective import Adjective
from panoptes.ling.tree.common.existential_there import ExistentialThere
from panoptes.ling.tree.common.number import Number
from panoptes.ling.tree.common.personal_pronoun import PersonalPronoun, \
    PersonalPronounCase
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.common.time_of_day import TimeOfDay
from panoptes.ling.tree.common.util.selector import Correlative, Selector
from panoptes.ling.tree.surface.base import SayContext, SayState
from panoptes.ling.tree.surface.common_noun import SurfaceCommonNoun
from panoptes.ling.tree.surface.comparative import SurfaceComparative
from panoptes.ling.tree.surface.conjunction import SurfaceConjunction
from panoptes.ling.tree.surface.content_clause import Complementizer, \
    SurfaceContentClause
from panoptes.ling.tree.surface.direction import SurfaceDirection
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
            if rel == 'neg':
                if t.text == 'not':
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
            vv = [v for v in vv if v.can_be_in_root_clause()]
            if vv:
                yield verb_span_pair, vv


class ParseToSurface(object):
    """
    Object that converts parses to surface structure.
    """

    def __init__(self, comparative_mgr, det_pronoun_mgr, personal_mgr,
                 plural_mgr, pro_adverb_mgr, say_state, time_of_day_mgr,
                 verb_mgr):
        # For extracting the correct verb conjugation from subjects.
        self.arbitrary_idiolect = Idiolect()
        self.say_state = say_state
        self.subject_say_context = SayContext(
            prep=None, has_left=True, has_right=True, is_possessive=False)

        self.end_punct_clf = EndPunctClassifier()
        self.verb_extractor = VerbExtractor(verb_mgr)

        self.comparative_mgr = comparative_mgr
        self.det_pronoun_mgr = det_pronoun_mgr
        self.personal_mgr = personal_mgr
        self.plural_mgr = plural_mgr
        self.pro_adverb_mgr = pro_adverb_mgr
        self.time_of_day_mgr = time_of_day_mgr

        self.tag2recognize_arg = {
            'DT': self.recog_dt,
            'EX': self.recog_ex,
            'JJ': self.recog_jj,
            'JJR': self.recog_jjr,
            'NN': self.recog_nn,
            'NNS': self.recog_nns,
            'NNP': self.recog_nnp,
            'PRP': self.recog_prp,
            'WP': self.recog_wp,
        }

        self.tag2recognize_prep_arg = {
            'RB': self.recog_rb,
            'WRB': self.recog_wrb,
            'RBR': self.recog_rbr,
        }

        self.invalid_verb_arg_root_tags = set([
            '.',
            'VB',
        ])

        self.directions = """
            north south east west
            left right
        """.split()

    def recog_dt(self, root_token):
        nn = []
        for selector in self.det_pronoun_mgr.parse_pronoun(root_token.text):
            n = SurfaceCommonNoun(selector=selector)
            nn.append(n)
        return [(None, n) for n in nn]

    def recog_ex(self, root_token):
        p_n = (None, ExistentialThere())
        return [p_n]

    def recog_jj(self, root_token):
        return [(None, Adjective(root_token.text))]

    def recog_jjr(self, root_token):
        if len(root_token.downs) != 1:
            return []

        rel, child = root_token.downs[0]

        if rel != 'prep':
            return []

        if child.text != 'than':
            return []

        # Eg, "what is the castle [bigger than]?"
        if not child.downs:
            rr = []
            for degree, polarity, base in \
                    self.comparative_mgr.decode(None, root_token.text):
                n = SurfaceComparative(polarity, base, None)
                rr.append((None, n))
            return rr

        rel, child = child.downs[0]

        if rel != 'pobj':
            return []

        r = self.recognize_verb_arg(child)
        if r is None:
            return []
        pp_nn = r

        pp_nn = [p_n3 for p_n3 in pp_nn if not p_n3[0]]
        thans = [p_n4[1] for p_n4 in pp_nn]

        rr = []
        for degree, polarity, base in \
                self.comparative_mgr.decode(None, root_token.text):
            for than in thans:
                n = SurfaceComparative(polarity, base, than)
                rr.append((None, n))
        return rr

    def recog_time_of_day(self, root_token):
        if not root_token.downs:
            pre = None
        elif len(root_token.downs) == 1:
            rel, child = root_token.downs[0]
            pre = child.text
        else:
            return []

        rr = self.time_of_day_mgr.decode(pre, root_token.text)
        return [((TIME_PREP,), TimeOfDay(*r)) for r in rr]

    def recog_how_many_nn_head(self, root_token, noun, n2):
        many = None
        for rel, child in root_token.downs:
            if rel == 'amod' and child.text in ('few', 'many'):
                many = child
                break

        if not many:
            return []

        how = None
        for rel, child in many.downs:
            if rel == 'advmod' and child.text == 'how':
                how = child

        number = Number(None)

        correlative = Correlative.INDEF
        count_restriction = self.det_pronoun_mgr.cor2res_gno[correlative][0]
        selector = Selector.from_correlative(correlative, count_restriction)
        assert selector

        n = SurfaceCommonNoun(selector=selector, number=number, noun=noun)
        return [(None, n)]

    def recog_dt_nn_head(self, root_token, noun, gram_n2):
        """
        * (ADJS) NN(S)     "fat mice"
        * DT (ADJS) NN(S)  "the fat mice"
        """
        downs = [rel_child5 for rel_child5 in root_token.downs if rel_child5[0] not in ('cc', 'conj', 'prep')]
        if downs:
            dep, child = downs[0]
            if dep != 'det':
                return []

            s = child.text
            if s == 'a' or s == 'an':
                s = A_OR_AN

            maybe_selectors = self.det_pronoun_mgr.parse_determiner(s)

            selectors = []
            for maybe_selector in maybe_selectors:
                for sel in maybe_selector.restricted_to_grammatical_number(
                        gram_n2, self.det_pronoun_mgr.cor2res_gno):
                    selectors.append(sel)
        else:
            if gram_n2 == N2.SING:
                return []

            selector = Selector(
                Correlative.INDEF, N5.DUAL, N5.MANY, N5.DUAL, N5.MANY)
            selectors = [selector]

        attrs = []
        for dep, child in downs[1:]:
            if dep != 'amod':
                return []
            attrs.append(child.text)

        nn = []
        for selector in selectors:
            n = SurfaceCommonNoun(selector=selector, attributes=list(attrs),
                                  noun=noun)
            nn.append(n)

        return [(None, n) for n in nn]

    def recog_posdet_nn_head(self, root_token, noun, gram_n2):
        """
        * PRP$ (ADJS) NN(S)
        * WP$ (ADJS) NN(S)
        """
        downs = [rel_child6 for rel_child6 in root_token.downs if rel_child6[0] not in ('cc', 'conj', 'prep')]

        if not downs:
            return []

        rel, possessor = downs[0]
        if rel != 'pos':
            return []

        attrs = []
        for rel, child in downs[1:]:
            if rel != 'amod':
                return []
            attrs.append(child.text)

        nn = []
        for declension in self.personal_mgr.posdet_parse((possessor.text,)):
            pos = PersonalPronoun(declension, PersonalPronounCase.OBJECT)

            correlative = Correlative.DEF
            count_restriction = self.det_pronoun_mgr.cor2res_gno[correlative][0]
            selector = Selector.from_correlative(correlative, count_restriction)
            if not selector:
                continue
            for selector in selector.restricted_to_grammatical_number(
                    gram_n2, self.det_pronoun_mgr.cor2res_gno):
                n = SurfaceCommonNoun(possessor=pos, selector=selector,
                                      attributes=list(attrs), noun=noun)
                nn.append(n)
        return [(None, n) for n in nn]

    def recog_shortcut_head(self, root_token):
        pp_nn = []
        ss = root_token.text,
        for prep, selector, noun in self.pro_adverb_mgr.parse(ss):
            n = SurfaceCommonNoun(selector=selector, noun=noun)
            pp_nn.append((prep, n))
        return pp_nn

    def recog_common_noun_head(self, root_token, noun, n2):
        pp_nn = []
        pp_nn += self.recog_how_many_nn_head(root_token, noun, n2)
        pp_nn += self.recog_dt_nn_head(root_token, noun, n2)
        pp_nn += self.recog_posdet_nn_head(root_token, noun, n2)
        pp_nn += self.recog_shortcut_head(root_token)
        return pp_nn

    def recog_common_noun_tail(self, root_token):
        preps_optionss = []
        for rel, child in root_token.downs:
            if rel != 'prep':
                continue
            if len(child.downs) != 1:
                continue
            rel, grandchild = child.downs[0]
            if rel != 'pobj':
                continue
            r = self.recognize_verb_arg(grandchild)
            if r is None:
                return None
            pp_nn = r
            pp_nn = [p_n1 for p_n1 in pp_nn if not p_n1[0]]
            nn = [p_n2[1] for p_n2 in pp_nn]
            prep = child.text,
            preps_optionss.append((prep, nn))
        return preps_optionss

    def recog_common_noun(self, root_token, noun, n2):
        head_pp_nn = self.recog_common_noun_head(root_token, noun, n2)

        preps_optionss = self.recog_common_noun_tail(root_token)

        if not preps_optionss:
            return head_pp_nn

        rr = []
        tail_preps, tail_optionss = list(zip(*preps_optionss))
        for head_p, head_n in head_pp_nn:
            for tail_options in product(*tail_optionss):
                n = deepcopy(head_n)
                n.preps_nargs = list(zip(tail_preps, tail_options))
                rr.append((head_p, n))
        return rr

    def recog_direction(self, root_token):
        if root_token.text not in self.directions:
            return []

        z = len(root_token.downs)
        if z == 0:
            return []
        elif z == 1:
            (prep, of), = root_token.downs
        elif z == 2:
            (det, dt), (prep, of) = root_token.downs
            if det != 'det':
                return []
            if dt.tag != 'DT':
                return []
        else:
            return []

        if prep != 'prep':
            return []

        if of.text != 'of':
            return []

        # Eg, "what is the castle [east of _]?"
        if not of.downs:
            n = SurfaceDirection(root_token.text, None)
            return [(None, n)]

        dep, child = of.downs[0]

        if dep != 'pobj':
            return []

        r = self.recognize_verb_arg(child)
        if r is None:
            return None
        pp_nn = r

        pp_nn = [p_n7 for p_n7 in pp_nn if not p_n7[0]]
        ofs = [p_n8[1] for p_n8 in pp_nn]

        pp_nn = []
        for of in ofs:
            d = SurfaceDirection(root_token.text, of)
            pp_nn.append((None, d))
        return pp_nn

    def recog_nn(self, root_token):
        """
        Eg, cat.
        """
        rr = self.recog_time_of_day(root_token)
        if rr:
            return rr

        rr = self.recog_direction(root_token)
        if rr:
            return rr

        sing = root_token.text
        rr = self.recog_common_noun(root_token, sing, N2.SING)
        return rr

    def recog_nns(self, root_token):
        """
        Eg, cats.
        """
        rr = []
        for sing in self.plural_mgr.to_singular(root_token.text):
            for r in self.recog_common_noun(root_token, sing, N2.PLUR):
                rr.append(r)
        return rr

    def recog_nnp(self, root_token):
        """
        Eg, James.
        """
        name = root_token.text,
        n = ProperNoun(name=name, is_plur=False)
        return [(None, n)]

    def recog_prp(self, root_token):
        """
        Eg, you.
        """
        ss = root_token.text,
        nn = self.personal_mgr.perspro_parse(ss)
        return [(None, n) for n in nn]

    def recog_wp(self, root_token):
        """
        Eg, who.
        """
        nn = []

        # For WP like "what".
        for selector in self.det_pronoun_mgr.parse_pronoun(root_token.text):
            n = SurfaceCommonNoun(selector=selector)
            nn.append(n)

        # For WP like "who".
        ss = root_token.text,
        nn += self.personal_mgr.perspro_parse(ss)

        return [(None, n) for n in nn]

    def recog_adverb(self, root_token):
        """
        We don't normally bother with adverbs, but do recognize pro-adverbs as
        actually being (prep, argument) pairs encoded into a single word.
        """
        return self.recog_shortcut_head(root_token)

    def recog_rb(self, root_token):
        """
        Eg, here.

        Returns None on failure (regular adverb, which we don't accept as args
        yet).
        """
        rr = self.recog_adverb(root_token)
        if rr:
            return rr

        return None

    def recog_wrb(self, root_token):
        """
        Eg, where.
        """
        return self.recog_adverb(root_token)

    def recog_rbr(self, root_token):
        """
        For bAbi, as a verb argument, just present in invalid parses?
        """
        return None

    def recognize_verb_arg(self, root_token):
        """
        Token -> None or list of (prep or None, SurfaceArgument)

        Returns None if we reject (do not recognize as an arg) the arg.
        """
        while True:
            f = self.tag2recognize_arg.get(root_token.tag)
            if f:
                rr = f(root_token)
                break

            f = self.tag2recognize_prep_arg.get(root_token.tag)
            if f:
                rr = f(root_token)
                break

            if root_token.tag in self.invalid_verb_arg_root_tags:
                rr = []
                break

            print('Unknown tag:', root_token.tag)
            assert False

        if not rr:
            return rr

        op = None
        for rel, child in root_token.downs:
            if rel != 'cc':
                continue

            op = STR2CONJUNCTION.get(child.text)
            break
        if not op:
            return rr

        for rel, child in root_token.downs:
            if rel == 'conj':
                # TODO: generalize this later.
                other_pp_nn = self.recognize_verb_arg(child)
                if not other_pp_nn:
                    return other_pp_nn
                rr2 = []
                for prep, n in rr:
                    for other_prep, other_n in other_pp_nn:
                        r2 = prep, SurfaceConjunction(op, [n, other_n])
                        rr2.append(r2)
                return rr2

        return rr

    def find_subject(self, verb_span_pair, varg_root_indexes):
        """
        args -> (subj arg index, vmain index) or None if impossible
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
            # We must have args.  Otherwise, it's not possible.
            if not varg_root_indexes:
                return None

            # Just the pre span ("would you?"): find the argument directly
            # after the verb words.
            for i, arg in enumerate(varg_root_indexes):
                if a[1] < arg:
                    return i, i + 1

            # If there are no args afterward, it isn't possible.
            return None
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
        (root token, verb span pair) -> args or None if impossible

        Where args are (subj arg index, vmain idx, options per arg), where an
        option is a (prep, verb arg).
        """
        varg_root_indexes = []
        ppp_nnn = []
        adverbs = []
        for rel, t in root_token.downs:
            if rel not in ('nsubj', 'nsubjpass', 'agent', 'dobj', 'dative',
                           'expl', 'attr', 'advmod', 'prep', 'compound',
                           'npadvmod', 'acomp'):
                continue

            if rel == 'advmod':
                for rel, down in t.downs:
                    if down.text == 'no':
                        adverbs.append(down.text)
                if t.text == 'longer':
                    adverbs.append(t.text)
                    continue

            if rel == 'agent':
                prep = 'by',
                if not t.downs:
                    pp_nn = [(prep, None)]
                    ppp_nnn.append(pp_nn)
                    varg_root_indexes.append(t.index)
                    continue
                assert len(t.downs) == 1
                rel, down = t.downs[0]
                assert rel == 'pobj'
                t = down
            elif t.tag == 'IN':
                if t.downs:
                    # Skip the conjunctions.
                    downs = [rel_child for rel_child in t.downs if rel_child[0] == 'pobj']
                    if len(downs) != 1:
                        continue
                    prep = t.text,
                    t = downs[0][1]
                else:
                    p = t.text,
                    pp_nn = [(p, None)]
                    ppp_nnn.append(pp_nn)
                    varg_root_indexes.append(t.index)
                    continue
            else:
                prep = None

            r = self.recognize_verb_arg(t)
            if r is None:
                continue
            pp_nn = r

            """
            if rel == 'npadvmod':
                for i, (p, n) in enumerate(pp_nn):
                    if not p:
                        pp_nn[i] = (TIME_PREP,), n
            """

            spoken_preps = [prep] * len(pp_nn)
            absorbed_preps, vargs = list(zip(*pp_nn)) if pp_nn else ([], [])
            pp_nn = []
            for spoken_prep, absorbed_prep, varg in \
                    zip(spoken_preps, absorbed_preps, vargs):
                if spoken_prep:
                    prep = spoken_prep
                elif absorbed_prep:
                    prep = absorbed_prep
                else:
                    prep = None
                pp_nn.append((prep, varg))

            ppp_nnn.append(pp_nn)

            varg_root_indexes.append(t.index)

        r = self.find_subject(verb_span_pair, varg_root_indexes)
        if r is None:
            return None
        subj_argx, vmain_index = r

        return subj_argx, vmain_index, ppp_nnn, adverbs

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
        subj_n = pp_nn[subj_argx][1]
        conj = subj_n.decide_conjugation(
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
                vv = [v for v in vv if not v.is_imperative()]
            if not vv:
                continue

            r = self.extract_verb_args(root_token, verb_span_pair)
            if r is None:
                continue
            subj_argx, vmain_index, ppp_nnn, adverbs = r

            if subj_argx is None:
                vv = [v for v in vv if v.is_imperative()]
            else:
                assert 0 <= subj_argx < len(ppp_nnn)

            for v in vv:
                for pp_nn in product(*ppp_nnn):
                    pp_nn = list(pp_nn)
                    for conj in self.possible_conjugations(v, pp_nn, subj_argx):
                        complementizer = Complementizer.ZERO
                        new_v = deepcopy(v)
                        new_v.conj = conj
                        c = SurfaceContentClause(
                            complementizer, new_v, adverbs, deepcopy(pp_nn),
                            vmain_index)
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
            if '?' in end_punct and clause.verb.is_imperative():
                continue
            yield SurfaceSentence(clause, end_punct)
