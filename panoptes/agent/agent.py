from panoptes.ling.english import Recognition


class Deliberation(object):
    def __init__(self, recognized, out=None):
        self.recognized = recognized
        assert isinstance(self.recognized, Recognition)

        self.out = None
        if self.out:
            assert isinstance(self.out, str)


class Agent(object):
    def reset(self):
        """
        ->

        Reset all the state.  Forget everything ever known.
        """
        raise NotImplementedError

    def new_user(self):
        """
        -> user ID int

        Create a new user.  Returns an unique user identifier.
        """
        raise NotImplementedError

    def put(self, uid, s):
        """
        (user ID int, text) -> Deliberation

        Receive input and maybe respond; also return information about what we
        did.
        """
        raise NotImplementedError
