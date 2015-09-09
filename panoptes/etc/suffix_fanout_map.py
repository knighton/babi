def each_suffix_shortest_first(s):
    for i in xrange(len(s) + 1): 
        yield s[len(s) - i:] 


class SuffixFanoutMap(object):
    """
    A suffix tree that does not generalize to shortened suffixes, only longer.

    If you can derive from a mountain of data containing all the exceptions and
    non-exceptional cases, use GeneralizingSuffixMap instead.  if you can (a)
    provide all the exceptions, and (b) the general rules, then use this.

    Example: in pluralization, there is a limitless number of plurals, quite a
    few exceptions, and not many pluralization rules.  Throwing those in a
    GeneralizingSuffixTree would screw it up due to the lack of normal examples
    to contain the scope of the exceptions.
    """

    def __init__(self, suffix2value, root_value, pick_value):
        self.suffix2value = suffix2value
        self.root_value = root_value
        self.pick_value = pick_value
        self.max_key_len = max(map(len, suffix2value.iterkeys()))

    def get(self, s):
        values = []
        for suffix in each_suffix_shortest_first(s):
            if suffix not in self.suffix2value:
                continue
            value = self.suffix2value[suffix]
            values.append(value)

        if values:
            return reduce(self.pick_value, values)

        return self.root_value
