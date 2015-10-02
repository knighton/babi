class LocationHistoryItem(object):
    def current_location(self):
        """
        -> location idea index or None if we don't know
        """
        raise NotImplementedError

    def is_at_location(self, loc_x):
        """
        location idea index -> True, False, or None for "I don't know"
        """
        raise NotImplementedError


class At(LocationHistoryItem):
    def __init__(self, x):
        self.x = x

    def dump(self):
        return {
            'type': 'At',
            'x': self.x,
        }

    def current_location(self):
        return self.x

    def is_at_location(self, there):
        if self.x == there:
            return True
        else:
            return False


class NotAt(LocationHistoryItem):
    def __init__(self, x):
        self.x = x

    def dump(self):
        return {
            'type': 'NotAt',
            'x': self.x,
        }

    def current_location(self):
        return None

    def is_at_location(self, there):
        if self.x == there:
            return False
        else:
            return None


class LocationHistory(object):
    def __init__(self):
        self.history = []

    def dump(self):
        return {
            'history': map(lambda h: h.dump(), self.history),
        }

    def update_location(self, location):
        self.history.append(location)

    def is_at_location(self, x):
        if not self.history:
            return None

        loc = self.history[-1]
        return loc.is_at_location(x)

    def current_location(self):
        if not self.history:
            return None

        loc = self.history[-1]
        return loc.current_location()
