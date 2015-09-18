# Purpose in communicating.
#
# Whether you're giving or receiving information.  Mostly about kinds of
# questions.
#
# Used for deciding sentence-ending punctuation, whether to do-split a verb, if
# there are wh-roles to possibly front, etc.

from collections import defaultdict

from panoptes.etc.combinatorics import each_choose_one_from_each
from panoptes.etc.enum import enum


Purpose = enum('Purpose = WH_Q TF_Q VERIFY_Q INFO')


class PurposeInfo(object):
    def __init__(self, purpose, has_q_args, override_split_verb_yes,
                 unstressed_end_punct, stressed_end_punct, is_ind_cond_only):
        # Enum value of this purpose.
        self.purpose = purpose
        assert Purpose.is_valid(self.purpose)

        # Whether question words must or must not be in a clause with this
        # intent.
        self.has_q_args = has_q_args
        assert isinstance(self.has_q_args, bool)

        # Whether to split the verb words ("don't you know" vs "you don't
        # know").  Splits on has_q_args unless override=yes is true (for T/F
        # questions).
        self.override_split_verb_yes = override_split_verb_yes
        assert isinstance(self.override_split_verb_yes, bool)

        # Sentence-ending punctuation.
        self.unstressed_end_punct = unstressed_end_punct
        self.stressed_end_punct = stressed_end_punct
        assert isinstance(self.unstressed_end_punct, str)
        assert isinstance(self.stressed_end_punct, str)

        # Whether the linguistic mood/modality must be either indicative or
        # conditional.  (Only restrict like this when you're asking questions or
        # verifying information).
        self.is_ind_cond_only = is_ind_cond_only
        assert isinstance(self.is_ind_cond_only, bool)

    def decide_end_punct(self, is_stressed):
        """
        whether stressed -> sentence-ending punctuation
        """
        return (self.stressed_end_punct if is_stressed else
                self.unstressed_end_punct)

    def split_verb(self, is_fronting):
        """
        whether fronting -> whether to split the verb
        """
        if self.override_split_verb_yes:
            return True

        return is_fronting

    def decode_end_punct(self, end_punct):
        rr = []
        if end_punct == self.stressed_end_punct:
            rr.append((self.purpose, True))
        if end_punct == self.unstressed_end_punct:
            rr.append((self.purpose, False))
        return rr


class PurposeManager(object):
    def __init__(self):
        data = """
            WH_Q      T  F  ?  ??  T
            TF_Q      F  T  ?  ??  T
            VERIFY_Q  F  F  ?  ?!  T
            INFO      F  F  .  !   F
        """

        # Purpose -> info.
        self.purpose2info = {}
        for line in data.strip().split('\n'):
            purpose, q_args, override_split, punct, stressed_punct, ind_only = \
                line.split()
            purpose = Purpose.from_str[purpose]
            has_q_args = True if q_args == 'T' else False
            override_split = True if override_split == 'T' else False
            ind_only = True if ind_only == 'T' else False
            info = PurposeInfo(purpose, has_q_args, override_split, punct,
                               stressed_punct, ind_only)
            self.purpose2info[purpose] = info

        # End punct -> purpose.
        self.punct2purposes = defaultdict(list)
        for info in self.purpose2info.itervalues():
            self.punct2purposes[info.unstressed_end_punct].append(info.purpose)
            self.punct2purposes[info.stressed_end_punct].append(info.purpose)

        # (has_q_args, is_split, is_fronting, is_ind_cond) -> possible Purposes.
        self.args2purposes = defaultdict(list)
        bools = [False, True]
        options = [
            bools,  # has_q_args
            bools,  # is_split
            bools,  # is_fronting
            bools,  # is_ind_cond
        ]
        for args in each_choose_one_from_each(options):
            has_q_args, is_split, is_fronting, is_ind_cond = args
            for info in self.purpose2info.itervalues():
                if has_q_args != info.has_q_args:
                    continue

                if info.is_ind_cond_only and not is_ind_cond:
                    continue

                if info.override_split_verb_yes:
                    if not is_split:
                        continue
                else:
                    if is_split != is_fronting:
                        continue

                if is_fronting and not has_q_args:
                    continue

                self.args2purposes[tuple(args)].append(info.purpose)

    def get(self, purpose):
        return self.purpose2info[purpose]

    def decode(self, has_q_args, is_verb_split, is_fronting, is_ind_or_cond,
               end_punct):
        """
        args -> list of (Purpose, is_stressed)
        """
        key = (has_q_args, is_verb_split, is_fronting, is_ind_or_cond)
        purposes = self.args2purposes[key]

        if end_punct:
            rr = []
            for purpose in purposes:
                rr += self.get(purpose).decode_end_punct(end_punct)
        else:
            purposes = filter(lambda p: p == Purpose.INFO, purposes)
            rr = map(lambda p: (p, False), purposes)
        return rr


class EndPunctClassifier(object):
    def classify(self, token):
        """
        Canonicalize sentence-ending punctuation.

            ??#?!?#?!! -> ?!
        """
        counts = defaultdict(int)
        for c in token:
            counts[c] += 1

        q = counts['?']
        e = counts['!']
        if q:
            if e:
                return '?!'
            elif 1 < q:
                return '??'
            else:
                return '?'
        elif e:
            return '!'
        else:
            return '.'
