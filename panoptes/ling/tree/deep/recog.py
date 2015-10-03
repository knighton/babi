from itertools import product

from panoptes.ling.glue.purpose import PurposeManager
from panoptes.ling.glue.relation import RelationManager
from panoptes.ling.tree.base import ArgPosRestriction
from panoptes.ling.tree.common.base import CommonArgument
from panoptes.ling.tree.common.proper_noun import ProperNoun
from panoptes.ling.tree.deep.common_noun import DeepCommonNoun
from panoptes.ling.tree.deep.content_clause import DeepContentClause, Status
from panoptes.ling.tree.deep.direction import DeepDirection
from panoptes.ling.tree.deep.sentence import DeepSentence
from panoptes.ling.tree.surface.sentence import SurfaceSentence
from panoptes.ling.verb.verb import ModalFlavor, Voice


class RecogContext(object):
    def __init__(self, end_punct, is_inside_an_if):
        # Ending punctuation token.  Matters for Purpose.
        #
        # Will be None if not the root clause of the sentence.
        self.end_punct = end_punct

        # Modality restrictions ("if I [were] a cat, I [would be] a cat").
        self.is_inside_an_if = is_inside_an_if


class SurfaceToDeep(object):
    """
    Object that converts surface structure to deep structure.
    """

    def __init__(self, purpose_mgr, relation_mgr):
        self.purpose_mgr = purpose_mgr
        assert isinstance(self.purpose_mgr, PurposeManager)

        self.relation_mgr = relation_mgr
        assert isinstance(self.relation_mgr, RelationManager)

        self.type2recog = {
            'SurfaceCommonNoun': self.recog_common_noun,
            'SurfaceDirection': self.recog_surface_direction,
        }

    def recog_common_noun(self, n):
        if n.possessor:
            poss = self.recog_arg(n.possessor)
        else:
            poss = [None]

        rr = []
        for pos in poss:
            assert not n.attributes
            assert not n.preps_nargs
            r = DeepCommonNoun(
                possessor=pos, selector=n.selector, number=n.number,
                noun=n.noun)
            rr.append(r)
        return rr

    def recog_surface_direction(self, n):
        if n.of:
            ofs = self.recog_arg(n.of)
        else:
            ofs = []

        return map(lambda of: DeepDirection(n.which, of), ofs)

    def decide_prep(self, fronted_prep, stranded_prep):
        """
        One or the other or neither must exist, but not both.
        """
        if fronted_prep:
            if stranded_prep:
                assert False
            else:
                prep = fronted_prep
        else:
            if stranded_prep:
                prep = stranded_prep
            else:
                prep = None
        return prep

    def unfront(self, hallu_preps_vargs, front_argx, subj_argx):
        """
        preps_vargs, indexes -> new preps_vargs, new subject argx

        Undo fronting.
        """
        assert 0 <= subj_argx < len(hallu_preps_vargs)
        if front_argx:
            assert front_argx + 1 == subj_argx

        if front_argx is None:
            return hallu_preps_vargs, subj_argx

        fronted_prep, fronted_arg = hallu_preps_vargs[front_argx]

        rr = hallu_preps_vargs[:front_argx]
        rr.append(hallu_preps_vargs[subj_argx])
        used_fronted = False
        for i in xrange(subj_argx + 1, len(hallu_preps_vargs)):
            prep, arg = hallu_preps_vargs[i]
            if arg:
                if arg.has_hole():
                    arg.put_fronted_arg_back(fronted_arg)
                    used_fronted = True
            else:
                assert not used_fronted
                arg = fronted_arg
                stranded_prep = prep
                prep = self.decide_prep(fronted_prep, stranded_prep)
            rr.append([prep, arg])

        if not used_fronted:
            rr.append([fronted_prep, fronted_arg])

        return rr, subj_argx - 1

    def decide_possible_relations(self, unfronted_preps_vargs, voice):
        preps_types = map(lambda (p, n): (p, n.relation_arg_type()),
                          unfronted_preps_vargs)
        return self.relation_mgr.decide_relation_options(
            preps_types, voice == Voice.ACTIVE)

    def recog_arg(self, arg):
        if isinstance(arg, CommonArgument):
            return [arg]

        key = arg.__class__.__name__
        return self.type2recog[key](arg)

    def recog_content_clause(self, c, context):
        """
        SurfaceContentClause -> list of DeepContentClause
        """
        if c.is_subjunctive() and not context.is_inside_an_if:
            return []

        front_argx = c.get_fronted_argx()

        has_q_args = False
        for p, n in c.preps_vargs:
            if n and n.is_interrogative():
                has_q_args = True
                break
        is_verb_split = c.verb.is_split
        is_fronting = front_argx is not None
        is_ind_or_cond = c.is_ind_or_cond()
        purposes_isstresseds = self.purpose_mgr.decode(
            has_q_args, is_verb_split, is_fronting, is_ind_or_cond,
            context.end_punct)

        status = Status.ACTUAL

        rr = []
        for hallu_preps_vargs, subj_argx in c.hallucinate_preps_vargs():
            unfronted_preps_vargs, subj_argx = \
                self.unfront(hallu_preps_vargs, front_argx, subj_argx)

            relation_options_per_arg = self.decide_possible_relations(
                unfronted_preps_vargs, c.verb.voice)
            if not relation_options_per_arg:
                return []

            deep_options_per_arg = \
                map(self.recog_arg,
                    map(lambda (p, n): n, unfronted_preps_vargs))

            for purpose, is_intense in purposes_isstresseds:
                for deeps in product(*deep_options_per_arg):
                    ok = True
                    for i, deep in enumerate(deeps):
                        res = deep.arg_position_restriction()
                        if res == ArgPosRestriction.SUBJECT:
                            if i != subj_argx:
                                ok = False
                                break
                        elif res == ArgPosRestriction.NOT_SUBJECT:
                            if i == subj_argx:
                                ok = False
                                break
                        elif res == ArgPosRestriction.ANYWHERE:
                            pass
                        else:
                            assert False
                    if not ok:
                        continue

                    for rels in product(*relation_options_per_arg):
                        rels_vargs = zip(rels, deeps)
                        r = DeepContentClause(
                            status, purpose, is_intense, c.verb.intrinsics,
                            c.adverbs, rels_vargs, subj_argx)
                        rr.append(r)
        return rr

    def recog(self, ssen):
        assert isinstance(ssen, SurfaceSentence)
        context = RecogContext(end_punct=ssen.end_punct, is_inside_an_if=False)
        rr = []
        for root in self.recog_content_clause(ssen.root, context):
            r = DeepSentence(root)
            rr.append(r)
        return rr
