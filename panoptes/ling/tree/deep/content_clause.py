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


# TODO: replace this with a method in all deep args.
def relation_arg_type_from_arg(a):
    if isinstance(a, DeepContentClause) and a.verb.verb_form == VerbForm.FINITE:
        return RelationArgType.FINITE_CLAUSE
    else:
        return RelationArgType.THING


def is_you(you):
    if not isinstance(you, PersonalPronoun):
        return False

    return you.declension in (Declension.YOU, Declension.YALL)


def transform(orig_preps_vargs, subj_index, is_imperative, argx_to_front,
              strand_fronted_prep):
    """
    args -> (transformed preps_vargs, vmain index)
    """

    if is_imperative:
        you = orig_preps_vargs[subj_index][1]
        assert is_you(you)

    if argx_to_front is not None:
        assert subj_index < argx_to_front

    rr = []

    # Pre-args.
    for prep, arg in orig_preps_args[:subj_index]:
        rr.append((pre, arg))

    # Fronted arg.
    stranded_prep = None
    if argx_to_front is not None:
        if strand_fronted_prep:
            stranded_prep, n = orig_preps_vargs[argx_to_front]
            fronted_prep = None
        else:
            fronted_prep, n = orig_preps_vargs[argx_to_front]
        rr.append((fronted_prep, n))

    # Subject.
    if not is_imperative:
        rr.append(orig_preps_vargs[subj_index])

    # Now calculate vmain_index.
    vmain_index = len(rr)

    # Post-args.
    for x in xrange(subj_index + 1, len(orig_preps_vargs)):
        prep, arg = orig_preps_vargs[x]
        if x == argx_to_front:
            if stranded_prep:
                rr.append((stranded_prep, None))
        else:
            rr.append((prep, arg))

    return rr, vmain_index


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

    def to_surface(self, state, idiolect):
        argx_to_front = decide_arg_to_front(
            self.rels_vargs, self.purpose, self.subj_index)

        # Verb context.
        voice = self.decide_voice()
        conj = self.decide_conjugation(idiolect)
        assert conj
        is_fronting = argx_to_front is not None
        is_split = state.purpose_mgr.purpose2info[self.purpose].split_verb(
            is_fronting)
        relative_cont = RelativeContainment.NOT_REL
        contract_not = idiolect.contractions
        split_inf = idiolect.split_infinitive
        if idiolect.subjunctive_were:
            sbj_handling = SubjunctiveHandling.WERE_SBJ
        else:
            sbj_handling = SubjunctiveHandling.WAS_SBJ
        surface_verb = SurfaceVerb(
            self.verb, voice, conj, is_split, relative_cont, contract_not,
            split_inf, sbj_handling)
        surface_verb.check(allow_wildcards=False)

        # Figure out prepositions for our relations.
        rels_types = []
        for rel, arg in self.rels_vargs:
            arg_type = relation_arg_type_from_arg(arg)
            rels_types.append((rel, arg_type))
        preps = state.relation_mgr.decide_preps(rels_types)

        # Build list of properly prepositioned surface arguments (without
        # fronting or imperative subject omission).
        orig_preps_surfs = []
        for (rel, arg), prep in zip(self.rels_vargs, preps):
            surface = arg.to_surface(sttae, idiolect)
            orig_preps_surfs.append((prep, surface))

        # If imperative, we disappear the subject ("do this" vs "you do this").
        is_imperative = self.verb.modality.flavor == ModalFlavor.IMPERATIVE

        # Apply transformations to get surface structure for args (eg,
        # fronting).
        preps_surfs, vmain_index = transform(
            orig_preps_surfs, self.subj_index, is_imperative, argx_to_front,
            idiolect.stranding)

        # Get the complementizer.
        ctzr = STATUS2COMPLEMENTIZER[self.status]

        return SurfaceContentClause(
            ctzr, surface_verb, preps_surfs, vmain_index)