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

    def to_surface(self, idiolect):
        assert False  # TODO
