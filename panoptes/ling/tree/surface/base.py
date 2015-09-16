from panoptes.ling.glue.inflection import Conjugation
from panoptes.ling.tree.base import BaseArgument


class SayState(object):
    """
    Extrinsic information needed to say verb arguments.

    Eg, I + reflexive = "me".
    """

    def __init__(self, correlative_mgr, inflection_mgr, personal_mgr,
                 plural_mgr, shortcut_mgr, verb_mgr):
        self.correlative_mgr = correlative_mgr  # CorrelativeManager.
        self.inflection_mgr = inflection_mgr    # InflectionManager.
        self.personal_mgr = personal_mgr        # PersonalManager.
        self.plural_mgr = plural_mgr            # PluralManager.
        self.shortcut_mgr = shortcut_mgr        # ShortcutManager.
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


class SurfaceArgument(BaseArgument):
    """
    An argument in surface structure.
    """

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
