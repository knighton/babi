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
        """
        location idea index ->

        Update our location.
        """
        self.history.append(location)

    def is_at_location(self, x):
        """
        location idea index -> True, False, or None if we don't know

        Tell whether we are at the given location.
        """
        if not self.history:
            return None

        loc = self.history[-1]
        return loc.is_at_location(x)

    def current_location(self):
        """
        -> location idea index or None if we don't know

        Get our current location.
        """
        if not self.history:
            return None

        loc = self.history[-1]
        return loc.current_location()

    def location_before(self, loc_x):
        """
        locatiion idea index -> location idea index or None if we don't know

        Get where we were most recently before we were at the given location.
        """
        print 'EVAL LOCATION BEFORE'
        import json
        print json.dumps(self.dump(), indent=4, sort_keys=True)
        for i in xrange(len(self.history) - 1, -1, -1):
            h = self.history[i]
            if not h.is_at_location(loc_x):
                continue

            if not i:
                return None

            h = self.history[i - 1]
            if not isinstance(h, At):
                continue

            return h.x
