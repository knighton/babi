from panoptes.etc.enum import enum
from panoptes.ling.glue.purpose import Purpose
from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.verb.verb import DeepVerb


# The truth value of the clause.
#
# Examples:
# * "I know [that] you did it last summer"
# * "I know [whether] you did it last summer"
Status = enum('Status = ACTUAL WHETHER')


COMPLEMENTIZER2STATUS = {
    Complementizer.ZERO: Status.ACTUAL,
    Complementizer.THAT: Status.ACTUAL,
    Complementizer.WHETHER: Status.WHETHER,
    Complementizer.IF: Status.WHETHER,
}


STATUS2COMPLEMENTIZER = {
    Status.ACTUAL: Complementizer.ZERO,
    Status.WHETHER: Complementizer.WHETHER,
}


def is_you(n):
    if not isinstance(n, PersonalPronoun):
        return False

    return n.declension in (Declension.YOU, Declension.YALL)


def decide_arg_to_front(rels_vargs, purpose, subj_index):
    # Only wh-questions might front.
    if purpose != Purpose.WH_Q:
        return None

    # Collect q-args.
    q = 0
    last = None
    for i, (r, n) in enumerate(rels_vargs):
        if n.is_interrogative():
            q += 1
            last = i

    # Don't front subjects.
    if q == 1 and last != subj_index:
        return last

    return None


class ContentClause(DeepArgument):
    def __init__(self, status, purpose, verb, rels_vargs, subj_index):
        self.status = status
        assert Status.is_valid(self.status)

        self.purpose = purpose
        assert Purpose.is_valid(self.purpose)

        self.verb = verb
        assert isinstance(self.verb, DeepVerb)

        self.rels_vargs = rels_vargs
        assert isinstance(self.rels_vargs, list)
        for r, n in self.rels_vargs:
            assert Relation.is_valid(r)
            assert isinstance(n, DeepArgument)

        # There must be at least one argument.
        assert self.rels_vargs

        # Subject is guaranteed to exist, including imperatives where the "you"
        # is omitted in the surface structure.
        self.subj_index = subj_index
        assert isinstance(self.subj_index, int)
        assert 0 <= self.subj_index < len(self.rels_vargs)

        # If imperative, subject must be "you".
        if self.verb.modality.flavor == ModalFlavor.IMPERATIVE:
            subj = self.rels_vargs[self.subj_index][1]
            assert is_you(subj)

        # Subject must be able to be the subject; other args must not be able to
        # not be the subject.
        for i, (r, n) in enumerate(self.rels_vargs):
            res = n.arg_position_restriction()
            if i == self.subj_index:
                cant_be = ArgPosRestriction.NOT_SUBJECT
            else:
                cant_be = ArgPosRestriction.SUBJECT
            assert res != cant_be

        # TODO: crosscheck purpose and wh-arg count.

    def decide_voice(self):
        subj_rel = self.rels_vargs[self.subj_index][0]
        if subj_rel == Relation.AGENT:
            return Voice.ACTIVE
        else:
            return Voice.PASSIVE

    def decide_conjugation(self, idiolect):
        subj = self.rels_vargs[self.subj_index][1]
        conj = subj.to_surface(idiolect).decide_conjugation()
        if conj is not None:
            return conj

        if len(self.rels_vargs) <= self.subj_index + 1:
            return None

        obj = self.rels_vargs[self.subj_index + 1][1]
        return obj.to_surface(idiolect).decide_conjugation()

    def to_surface(self, idiolect):
        argx_to_front = decide_arg_to_front(
            self.rels_vargs, self.purpose, self.subj_index)

        # Verb context.
        voice = self.decide_voice()
        conj = self.decide_conjugation(idiolect)
        assert conj
        is_fronting = argx_to_front is not None
        is_split = XXX
        relative_cont = RelativeContainment.NOT_REL
        contract_not = idiolect.contractions
        split_inf = idiolect.split_infinitive
        if idiolect.subjunctive_were:
            sbj_handling = SubjunctiveHandling.WERE_SBJ
        else:
            sbj_handling = SubjunctiveHandling.WAS_SBJ
        verb = SurfaceVerb(self.verb, voice, conj, is_split, relative_cont,
                           contract_not, split_inf, sbj_handling)
