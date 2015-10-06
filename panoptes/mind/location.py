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
        self.spans_items = []

    def dump(self):
        rr = []
        for span, item in self.spans_items:
            rr.append([span, item.dump()])
        return {
            'spans_items': rr,
        }

    def set_location(self, location):
        """
        location idea index ->

        Update our location.
        """
        if self.spans_items:
            span, item = self.spans_items[-1]
            if item.dump() == location.dump():
                return

        self.spans_items.append((None, location))

    def is_at_location(self, x):
        """
        location idea index -> True, False, or None if we don't know

        Tell whether we are at the given location.
        """
        if not self.spans_items:
            return None

        span, loc = self.spans_items[-1]
        return loc.is_at_location(x)

    def get_location(self):
        """
        -> location idea index or None if we don't know

        Get our current location.
        """
        if not self.spans_items:
            return None

        span, loc = self.spans_items[-1]
        return loc.current_location()

    def set_location_at_time(self, location, input_span):
        insert_before = 0
        for i, (span, item) in enumerate(self.spans_items):
            if input_span[0] < span[0]:
                insert_before = i

        self.spans_items = self.spans_items[:insert_before] + \
            [(input_span, location)] + self.spans_items[insert_before:]

    def get_location_before_location(self, loc_x):
        """
        locatiion idea index -> location idea index or None if we don't know

        Get where we were most recently before we were at the given location.
        """
        print 'EVAL LOCATION BEFORE'
        import json
        print json.dumps(self.dump(), indent=4, sort_keys=True)
        for i in xrange(len(self.spans_items) - 1, -1, -1):
            span, item = self.spans_items[i]
            if not item.is_at_location(loc_x):
                continue

            if not i:
                return None

            span, item = self.spans_items[i - 1]
            if not isinstance(item, At):
                continue

            return item.x
