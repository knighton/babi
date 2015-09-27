from panoptes.ling.english import Recognition


class Deliberation(object):
    def __init__(self, recognized):
        self.recognized = recognized
        assert isinstance(self.recognized, Recognition)


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
        (user ID int, text) -> (text or None, Deliberation)

        Receive input and maybe respond; also return information about what we
        did.
        """
        raise NotImplementedError
