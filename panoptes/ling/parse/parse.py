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

        # We don't like adverbial phrases.  We do like prepositional phrases as
        # verb arguments.
        #
        #   "Mary went back to the garden."
        #
        # Got
        #
        #   went -> back -> to -> garden -> the
        #
        # Want
        #
        #   * went -> back
        #   * went -> to -> garden -> the
        for t in self.tokens:
            # We want to transform
            #
            #   verb -advmod-> adverb -prep-> prep
            #
            # into
            #
            #   verb -advmod-> adverb
            #   verb -prep-> prep

            # Do the checks.
            if t.tag != 'IN':
                continue
            rel, parent = t.up
            if rel != 'prep':
                continue
            if parent is None:
                continue
            if parent.tag != 'RB':
                continue
            parent_rel, grandparent = parent.up
            if parent_rel != 'advmod':
                continue
            if grandparent is None:
                continue
            if not grandparent.tag.startswith('V'):
                continue

            # Do the tree surgery.
            for i, (_, child) in enumerate(parent.downs):
                if child.index == t.index:
                    del parent.downs[i]
                    break
            t.up = (rel, grandparent)
            grandparent.downs.append((rel, t))
            grandparent.downs.sort(key=lambda (dep, child): child.index)

        # Break up compounds of the form (determiner) (noun) (direction) (PP).
        #
        #   "What is the bathroom east of?"
        for t in self.tokens:
            rel, parent = t.up
            if parent is None:
                continue
            if rel != 'compound':
                continue
            parent_rel, grandparent = parent.up
            if grandparent is None:
                continue

            # Some generic relation for nouns that won't break surface recog.
            guess_rel = 'nsubj'

            # Give the child of the "compound" relation to its grandparent.
            for i, (_, child) in enumerate(parent.downs):
                if child.index == t.index:
                    del parent.downs[i]
                    break
            t.up = (guess_rel, grandparent)
            grandparent.downs.append((guess_rel, t))
            grandparent.downs.sort(key=lambda (dep, child): child.index)

            # Reassign its parent's det to it.
            det = None
            for i, (rel, down) in enumerate(parent.downs):
                if rel == 'det':
                    det = down
                    del parent.downs[i]
                    break
            if not det:
                continue
            t.downs.append(('det', det))
            t.downs.sort(key=lambda (dep, child): child.index)

        # Prepositional phrase attachment: should be owned by another arg.
        #
        #   "The hallway is south of the bedroom."
        for i in xrange(len(self.tokens) - 1):
            this = self.tokens[i]
            right = self.tokens[i + 1]
            if not (this.tag == 'NN' and right.tag == 'IN'):
                continue

            if right.text != 'of':
                continue

            rel, parent = right.up
            if parent.index == this.index:
                continue

            for i, (_, child) in enumerate(parent.downs):
                if child.index == right.index:
                    del parent.downs[i]
                    break

            right.up = (rel, this)

            this.downs.append((rel, right))
            this.downs.sort(key=lambda (rel, child): child.index)

        # Prepositional phrase attachment: should be its own arg.
        #
        #   "Where was the apple before the beach?"
        for t in self.tokens:
            if t.text != 'before':
                continue

            rel, parent = t.up
            if parent is None:
                continue
            if parent.tag != 'NN':
                continue
            parent_rel, grandparent = parent.up
            if grandparent is None:
                continue

            for i, (_, child) in enumerate(parent.downs):
                if child.index == t.index:
                    del parent.downs[i]
                    break
            parent.up = (rel, grandparent)
            grandparent.downs.append((rel, t))
            grandparent.downs.sort(key=lambda (dep, child): child.index)

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
            up_up.downs.sort(key=lambda (a, b): b.index)

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
            t.up[1].downs.sort(key=lambda (a, b): b.index)

        return self

    def dump(self):
        print 'Parse {'

        print '   ',
        for t in self.tokens:
            print '%d=%s/%s' % (t.index, t.text, t.tag),
        print

        def fix((rel, parent)):
            if parent:
                parent = parent.index
            return ' '.join(map(str, [rel, parent]))

        for t in self.tokens:
            print '   ', fix(t.up), '->', t.index, '->', map(fix, t.downs)

        print '}'
