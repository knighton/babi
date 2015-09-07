from ling.tree.surface.base import Argument


class ContentClause(Argument):
    def __init__(self, ctzr, verb, preps_vargs, vrest_index):
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
        #                           |         | vrest_index
        #                           |         |
        #                       pre verb  main verb
        #                       words     words
        #
        # At most one of the verb args can be None, due to being fronted.
        self.preps_vargs = preps_vargs  # List of (str tuple, Argument).

        # Index into preps_vargs of where the main verb words are to be
        # inserted.
        #
        # We use vrest_index and not subj_index because the subject is not
        # guaranteed to exist (imperatives, relative clauses, etc).
        #
        # When the verb words are pre-words only, the existence of the
        # subject is guaranteed, making it just an offset (eg, "do you?").
        # Pre-words only means the purpose is a question.  Relative clauses
        # cannot have that purpose.  So vrest_index works in all cases.
        self.vrest_index = vrest_index  # Int.

    def check(self):
        assert Complementizer.is_valid(self.ctzr)

        assert isinstance(self.verb, SurfaceVerb)

        missing_args = 0
        for p, n in self.preps_vargs:
            if p:
                assert isinstance(p, tuple)
            if n:
                assert isinstance(n, Argument)
                missing_args += 1
        assert missing_args in (0, 1)

        assert isinstance(self.vrest_index, int)
        assert 0 <= self.vrest_index <= len(self.preps_vargs)
