from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.surface.base import SurfaceArgument


Complementizer = enum('Complementizer = ZERO THAT WHETHER IF')


COMPLEMENTIZER2WORD = {
    Complementizer.ZERO: None,
    Complementizer.THAT: 'that',
    Complementizer.WHETHER: 'whether',
    Complementizer.IF: 'if',
}


class ContentClause(SurfaceArgument):
    def __init__(self, ctzr, verb, preps_vargs, vmain_index):
        # Complementizer.
        #
        # If we are the content of a relative clause, can only be ZERO.
        self.ctzr = ctzr  # Complementizer.

        # SurfaceVerb.  Some of its fields are tield to other parameters.
        self.verb = verb  # SurfaceVerb.

        # List of (prep, verb argument).
        #
        #    [0..2]     [3]           [4]       [5..8]
        #   (pre args) (fronted arg) (subject) (posts args)
        #                           |         | |
        #                           |         | vmain_index
        #                           |         |
        #                       pre verb  main verb
        #                       words     words
        #
        # At most one of the verb args can be None, due to being fronted.
        self.preps_vargs = preps_vargs  # List of (str tuple, SurfaceArgument).

        # Index into preps_vargs of where the main verb words are to be
        # inserted.
        #
        # We use vmain_index and not subj_index because the subject is not
        # guaranteed to exist (imperatives, relative clauses, etc).
        #
        # When the verb words are pre-words only, the existence of the subject
        # is guaranteed, making it just an offset (eg, "do you?").  Pre-words
        # only means that the purpose is a question.  Relative clauses cannot
        # have that purpose.  So vmain_index works in all cases.
        self.vmain_index = vmain_index  # Int.

    def check(self):
        assert Complementizer.is_valid(self.ctzr)

        assert isinstance(self.verb, SurfaceVerb)

        missing_args = 0
        for p, n in self.preps_vargs:
            if p:
                assert isinstance(p, tuple)
            if n:
                assert isinstance(n, SurfaceArgument)
                missing_args += 1
        assert missing_args in (0, 1)

        assert isinstance(self.vmain_index, int)
        assert 0 <= self.vmain_index <= len(self.preps_vargs)

    def decide_conjugation(self, state):
        return Conjugation.S3

    def say(self, state, context):
        ss = []

        # Get the complementizer, if any.
        s = COMPLEMENTIZER2WORD[self.ctzr]
        if s:
            ss.append(s)

        # Say the verb.
        #
        # If the verb words go in front, verb_pre_tokens (split-off verb words
        # that go in front of a subject instead of after like the rest) will be
        # empty.
        verb_pre_tokens, verb_main_tokens = state.verb_mgr.say(self.verb)

        # Say each verb argument.
        for i, (prep, varg) in enumerate(self.preps_vargs):
            if i == self.vmain_index - 1:
                ss += verb_pre_tokens
            elif i == self.vmain_index:
                ss += verb_main_tokens

            if varg:
                r = varg.say(state, sub_context)
                ss += r.tokens
        if self.vmain_index == len(self.preps_vargs):
            ss += verb_main_tokens

        # Eg, "[you going home] is ...".
        conj = Conjugation.S3

        return SayResult(tokens=ss, conjugation=conj, eat_prep=False)
