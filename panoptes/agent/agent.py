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
        (user ID int, text) -> text or None

        Receive input and maybe respond.
        """
        raise NotImplementedError
