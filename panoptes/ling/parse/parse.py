class Token(object):
    """
    A single token in a parse.
    """

    def __init__(self, index, text, tag, up, downs):
        self.index = index  # integer index
        self.text = text    # text
        self.tag = tag      # tag
        self.up = up        # (dep, Token or None)
        self.downs = downs  # list of (dep, Token)

    def to_d(self):
        return {
            'index': self.index,
            'text': self.text,
            'tag': self.tag,
        }


class Parse(object):
    """
    A parse tree.
    """

    def __init__(self, tokens, root):
        self.tokens = tokens  # list of Tokens
        self.root = root      # the root Token in tokens

    def fixed(self):
        """
        We completely give up on certain parse shapes.
        """
        for token in self.tokens:
            if token.tag == 'XX':
                return None

        # Handle verb args descended from an aux relation.
        for t in self.tokens:
            dep, up = t.up
            if up is None:
                continue
            up_dep, up_up = up.up
            if up_up is None:
                continue
            if up_dep != 'aux':
                continue
            for i, (_, child) in enumerate(up.downs):
                if child.index == t.index:
                    del up.downs[i]
                    break
            t.up = (dep, up_up)
            up_up.downs.append((dep, t))
            up_up.downs = sorted(up_up.downs, key=lambda (a, b): b)

        # Handle advmod descending from a noun (relative clauses?), when at
        # least in bAbi it is always descended from the verb.
        for t in self.tokens:
            dep, up = t.up
            if up is None:
                continue
            if dep != 'advmod':
                continue
            if up.tag != 'NN':
                continue

            # Do the tree surgery.
            for i, (_, child) in enumerate(up.downs):
                if child.index == t.index:
                    del up.downs[i]
                    break
            t.up = dep, up.up[1]
            t.up[1].downs.append((dep, t))
            t.up[1].downs = sorted(t.up[1].downs, key=lambda (a, b): b)

        return self

    def dump(self):
        print 'Parse {'

        for t in self.tokens:
            print '%d=%s/%s' % (t.index, t.text, t.tag),
        print

        def fix((rel, parent)):
            if parent:
                parent = parent.index
            return ' '.join(map(str, [rel, parent]))

        for t in self.tokens:
            print fix(t.up), '->', t.index, '->', map(fix, t.downs)

        print '}'
