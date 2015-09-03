class Token(object):
    """
    A single token in a parse.
    """

    def __init__(self, index, word, tag, up, downs):
        self.index = index  # integer index
        self.word = word    # word
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
