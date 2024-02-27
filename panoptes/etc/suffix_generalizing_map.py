class SuffixGeneralizingMapNode(object):
    """
    Node of a SuffixGeneralizingMap.
    """

    def __init__(self, keys, value, is_leaf):
        self.keys = keys
        self.value = value
        self.is_leaf = is_leaf


def prepad_str(s, max_len, c):
    """
    Pad the beginning of str 's' with 'max_len' instances of 'c'.
    """
    return c * (max_len - len(s)) + s


def each_suffix_shortest_first(s):
    """
    Get all possible suffixes in shortest-first order.
    """
    for i in range(len(s) + 1):
        yield s[len(s) - i:]


def each_suffix_longest_first(s):
    """
    Get all possible suffixes in longest-first order.
    """
    for i in range(len(s), -1, -1):
        yield s[len(s) - i:]


class SuffixGeneralizingMap(object):
    """
    Given a mapping of

        str -> value

    , define a suffix tree that generalizes the given examples in order to
    handle arbitrary strings.

    If ambiguous (if there are no examples of its suffix until reaching a parent
    suffix that maps to different values), calls a provided comparison function
    pick_value().

    Example: lemma -> which way to conjugate it.
    """

    def __init__(self, key2value, pick_value):
        self.max_key_len = max(list(map(len, key2value)))

        for key in key2value:
            assert '^' not in key

        # Build list of initial todos, which are (padded key, value).
        todos = list(zip(
            [prepad_str(s, self.max_key_len, '^') for s in key2value],
            iter(key2value.values())))

        # Loop around until done, splitting nodes to resolve conflicts.
        self.suffix2node = {}
        while todos:
            next_todos = []
            for key, value in todos:
                for suffix in each_suffix_shortest_first(key):
                    # If the suffix isn't in the tree, add myself here and
                    # we're done.
                    if not suffix in self.suffix2node:
                        is_leaf = True
                        self.suffix2node[suffix] = SuffixGeneralizingMapNode(
                            [key], value, is_leaf)
                        break

                    node = self.suffix2node[suffix]

                    # It's possible to find a node with the correct value, but
                    # that has a child with an even more accurate suffix but
                    # wrong value, which would screw up the lookup.
                    #
                    # So if the node is internal, keep branching.
                    if not node.is_leaf:
                        continue

                    # Leaf node: if we have the same value, we're good, but add
                    # myself to the keys (because we might need to split later).
                    if value == node.value:
                        node.keys.append(key)
                        break

                    # Else, we disagreed about what the value shoould be.
                    #
                    # Use the provided method to pick which value to keep here,
                    # throw its keys on the next round's todo list, and keep
                    # looking with a longer suffix.
                    next_todos += list(zip(list(node.keys),
                                      [node.value] * len(node.keys)))
                    picked_value = pick_value(value, node.value)
                    is_leaf = False
                    self.suffix2node[suffix] = SuffixGeneralizingMapNode(
                        [], picked_value, is_leaf)
                todos = next_todos

            # Tree building is done, so there's no more splitting to do, so
            # remove all the partial key lists.
            for suffix, node in self.suffix2node.items():
                if not node.is_leaf:
                    node.keys = []

    def get(self, key):
        s = prepad_str(key, self.max_key_len, '^')
        for suffix in each_suffix_longest_first(s):
            if suffix in self.suffix2node:
                return self.suffix2node[suffix].value
        assert False
