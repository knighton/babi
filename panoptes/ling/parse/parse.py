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


class Parse(object):
    """
    A parse tree.
    """

    def __init__(self, tokens, root):
        self.tokens = tokens  # list of Tokens
        self.root = root      # the root Token in tokens

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
