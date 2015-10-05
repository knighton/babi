from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.base import BaseArgument


class SayState(object):
    """
    Extrinsic information needed to say verb arguments.

    Eg, 1st person singular + reflexive = "me".
    """

    def __init__(self, comparative_mgr, det_pronoun_mgr, inflection_mgr,
                 personal_mgr, plural_mgr, pro_adverb_mgr, verb_mgr):
        self.comparative_mgr = comparative_mgr  # ComparativeManager.
        self.det_pronoun_mgr = det_pronoun_mgr  # CorrelativeManager.
        self.inflection_mgr = inflection_mgr    # InflectionManager.
        self.personal_mgr = personal_mgr        # PersonalManager.
        self.plural_mgr = plural_mgr            # PluralManager.
        self.pro_adverb_mgr = pro_adverb_mgr    # ShortcutManager.
        self.verb_mgr = verb_mgr                # VerbManager.


class SayContext(object):
    """
    The context that the argument is said in, that affect how it is said.
    """

    def __init__(self, prep, has_left, has_right, is_possessive):
        # The preposition matters because sometimes the argument absorbs the
        # preposition when it is said (eg, because of what reason -> why).
        self.prep = prep

        # When an object is to be delimited by commas on either side, you don't
        # if there is nothing on that side.
        self.has_left = has_left
        self.has_right = has_right

        # Whether it needs to be said in its possessive form.
        self.is_possessive = is_possessive

    def check(self):
        if self.prep is not None:
            assert self.prep
            assert isinstance(self.prep, list)

        assert isinstance(self.has_left, bool)
        assert isinstance(self.has_right, bool)

        assert isinstance(self.is_possessive, bool)


class SayResult(object):
    """
    Output from saying.
    """

    def __init__(self, tokens, conjugation, eat_prep):
        self.tokens = tokens            # List of str.
        self.conjugation = conjugation  # Conjugation.
        self.eat_prep = eat_prep        # bool.

    def check(self):
        assert isinstance(self.tokens, list)
        for s in self.tokens:
            assert isinstance(s, basestring)

        if self.conjugation is not None:
            assert Conjugation.is_valid(self.conjugation)

        assert isinstance(self.eat_prep, bool)

    def dump(self):
        return {
            'tokens': self.tokens,
            'conjugation': Conjugation.to_str[self.conjugation],
            'eat_prep': self.eat_prep,
        }


class SurfaceArgument(BaseArgument):
    """
    An argument in surface structure.
    """

    def has_hole(self):
        """
        -> bool

        Whether we contain a hole left by an internal that was fronted,  Used by
        deep recog.  Only possible with 'complex' arguments like noun phrases.

        Example: "What are you east of?"
        """
        return False

    def put_fronted_arg_back(self, n):
        """
        ->

        Put an internal that was extracted to be the fronted argument back into
        its original position.  Used by deep recog.  Only call this if
        has_hole() is True.

        Example: "What are you east of?" -> east of [what]
        """
        assert False

    def decide_conjugation(self, state, idiolect, context):
        """
        SayState, Idiolect, SayContext -> Conjugation or None

        Decide the conjugation of the verb, if we are the subject.  Check
        arg_position_restriction() first to verify we can actually be the
        subject (eg, "me").

        Returns None if we are ExistentialThere.  If we return None, the caller
        must get the conjugation from the object.

        Behavior is undefined if we cannot be a subject.

        Override this method in order to not have to say the full object
        (matters for complex objects like SurfaceContentClause,
        SurfaceCommonNoun, etc).

        TODO: SubjectConjugation enum.
        """
        return self.say(state, idiolect, context).conjugation

    def say(self, state, idiolect, context):
        """
        SayState, Idiolect, SayContext or None -> SayResult

        The context is None if we are not a standalone argument ("3 feet" vs "a
        3 foot wall").

        Render this object (words, conjugation if it's the subject, whether to
        drop the owning preposition).

        Nontrivial objects depend on external state to be said.
        """
        raise NotImplementedError
