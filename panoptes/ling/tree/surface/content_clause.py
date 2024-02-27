from panoptes.etc.enum import enum
from panoptes.ling.glue.inflection import Conjugation, Declension
from panoptes.ling.glue.relation import RelationArgType
from panoptes.ling.tree.common.personal_pronoun import PersonalPronoun, \
    PersonalPronounCase
from panoptes.ling.tree.surface.base import SayContext, SayResult, \
    SurfaceArgument
from panoptes.ling.verb.verb import SurfaceVerb


Complementizer = enum('Complementizer = ZERO THAT WHETHER IF')


COMPLEMENTIZER2WORD = {
    Complementizer.ZERO: None,
    Complementizer.THAT: 'that',
    Complementizer.WHETHER: 'whether',
    Complementizer.IF: 'if',
}


class SurfaceContentClause(SurfaceArgument):
    def __init__(self, complementizer, verb, adverbs, preps_vargs, vmain_index):
        # Complementizer.
        #
        # If we are the content of a relative clause, can only be ZERO.
        self.complementizer = complementizer  # Complementizer.

        # SurfaceVerb.  Some of its fields are tield to other parameters.
        self.verb = verb  # SurfaceVerb.

        # List of adverbs.
        self.adverbs = adverbs

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
        self.vmain_index = vmain_index  # int.

        assert Complementizer.is_valid(self.complementizer)

        assert isinstance(self.verb, SurfaceVerb)

        for s in self.adverbs:
            assert isinstance(s, str)

        missing_args = 0
        for p, n in self.preps_vargs:
            if p:
                assert isinstance(p, tuple)

            if n:
                assert isinstance(n, SurfaceArgument)
            else:
                missing_args += 1
        assert missing_args in (0, 1)

        assert isinstance(self.vmain_index, int)
        assert 0 <= self.vmain_index <= len(self.preps_vargs)

    def get_fronted_argx(self):
        """
        -> index or None

        Get the index of the fronted argument, if any.

        We will consider any interrogative argument right before the subject to
        have been fronted.
        """
        x = self.vmain_index - 2
        if not (0 <= x < len(self.preps_vargs)):
            return None

        n = self.preps_vargs[x][1]
        if not n.is_interrogative():
            return None

        return x

    def get_stranded_argx(self):
        """
        -> index or None

        Get the stranded index, if any.  The stranded index is where the fronted
        argument originally was, and still contains its preposition (due to
        preposition stranding) and a None for its argument.
        """
        for i in range(self.vmain_index, len(self.preps_vargs)):
            p, n = self.preps_vargs[i]
            if not n:
                return i
        return None

    def is_imperative(self):
        return self.verb.is_imperative()

    def is_ind_or_cond(self):
        return self.verb.is_ind_or_cond()

    def is_subjunctive(self):
        return self.verb.is_subjunctive()

    def hallucinate_preps_vargs(self):
        """
        -> yields (preps_vargs, subject index)

        Return versions of prep_vargs where we hallucinate the subject if it's
        missing (ie, imperatives), which is used for recog to deep structure.
        """
        if not self.is_imperative():
            subj_index = self.vmain_index - 1
            yield (self.preps_vargs, subj_index)
            return

        you_sing = PersonalPronoun(Declension.YOU, PersonalPronounCase.SUBJECT)
        you_plur = PersonalPronoun(Declension.YALL, PersonalPronounCase.SUBJECT)
        for you in [you_sing, you_plur]:
            pre = self.preps_vargs[:self.vmain_index]
            subject = (None, you)
            post = self.preps_vargs[self.vmain_index:]
            pp_nn = pre + [subject] + post
            yield pp_nn, self.vmain_index

    # --------------------------------------------------------------------------
    # From base.

    def dump(self):
        preps_vargs = []
        for prep, arg in self.preps_vargs:
            if arg:
                arg = arg.dump()
            preps_vargs.append([prep, arg])

        return {
            'type': 'SurfaceContentClause',
            'complementizer': Complementizer.to_str[self.complementizer],
            'verb': self.verb.dump(),
            'adverbs': self.adverbs,
            'preps_vargs': preps_vargs,
            'vmain_index': self.vmain_index,
        }

    def relation_arg_type(self):
        if self.verb.is_finite():
            return RelationArgType.FINITE_CLAUSE
        else:
            return RelationArgType.INERT

    # --------------------------------------------------------------------------
    # From surface.

    def decide_conjugation(self, state, idiolect, context):
        return Conjugation.S3

    def say(self, state, idiolect, context):
        ss = []

        # Get the complementizer, if any.
        ctzr = COMPLEMENTIZER2WORD[self.complementizer]
        if ctzr:
            ss.append(ctzr)

        # Say the verb.
        #
        # If the verb words go in front, verb_pre_tokens (split-off verb words
        # that go in front of a subject instead of after like the rest) will be
        # empty.
        verb_pre_tokens, verb_main_tokens = state.verb_mgr.say(self.verb)

        fronted_argx = self.get_fronted_argx()
        stranded_argx = self.get_stranded_argx()

        # Say each verb argument.
        ate_stranded_prep = False
        for i, (prep, varg) in enumerate(self.preps_vargs):
            if i == self.vmain_index - 1:
                ss += verb_pre_tokens
            elif i == self.vmain_index:
                ss += verb_main_tokens

            if varg:
                if context.has_left:
                    left = True
                elif ctzr:
                    left = True
                else:
                    left = 0 < i

                if context.has_right:
                    right = True
                elif i < len(self.preps_vargs) - 1:
                    right = True
                elif self.vmain_index == len(self.preps_vargs):
                    right = True
                else:
                    right = False

                used_stranded_prep = False
                if i == fronted_argx and not prep:
                    if stranded_argx:
                        used_stranded_prep = True
                        prep = self.preps_vargs[stranded_argx][0]

                sub_context = SayContext(
                    prep=prep, has_left=left, has_right=right,
                    is_possessive=False)

                r = varg.say(state, idiolect, sub_context)
                if prep and not r.eat_prep:
                    ss += prep
                ss += r.tokens

                if used_stranded_prep and r.eat_prep:
                    ate_stranded_prep = True
            else:
                if i != stranded_argx or not ate_stranded_prep:
                    ss += prep
        if self.vmain_index == len(self.preps_vargs):
            ss += verb_main_tokens

        # Eg, "[you going home] is ...".
        conj = Conjugation.S3

        return SayResult(tokens=ss, conjugation=conj, eat_prep=False)

    # --------------------------------------------------------------------------
    # Static.

    @staticmethod
    def load(d, loader):
        complementizer = Complementizer.from_str[d['complementizer']]
        verb = SurfaceVerb.load(d['verb'])

        preps_vargs = []
        for prep, arg in d['preps_vargs']:
            if arg:
                arg = loader.load(arg)
            preps_vargs.append((prep, arg))

        adverbs = d['adverbs']
        vmain_index = d['vmain_index']

        return SurfaceContentClause(
            complementizer, verb, adverbs, preps_vargs, vmain_index)
