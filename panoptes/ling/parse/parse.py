from collections import defaultdict


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


def reassign_parent(node, new_parent):
    rel, old_parent = node.up
    if old_parent:
        for i, (_, child) in enumerate(old_parent.downs):
            if child.index == node.index:
                del old_parent.downs[i]
                break

    node.up = rel, new_parent

    new_parent.downs.append((rel, node))
    new_parent.downs.sort(key=lambda (dep, child): child.index)


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
        print 'INPUT TO FIXED:'
        print
        print
        print
        self.dump()
        print
        print
        print

        for token in self.tokens:
            if token.tag == 'XX':
                return None

        # "Does (subject) (verb)"-style questions sometimes get parsed like the
        # (verb) is a noun, compounded to the true subject.  Requires much
        # fiddling to fix.
        while True:
            if self.root.text not in ['do', 'does', 'did']:
                break

            dobj = None
            has_aux = False
            for rel, child in self.root.downs:
                if rel == 'dobj':
                    dobj = child
                elif rel == 'aux':
                    has_aux = True
            if not dobj:
                break
            if has_aux:
                break
            if dobj.tag != 'NN':
                break

            # Fuck you too!
            self.root.up = 'aux', None
            for i, (rel, child) in enumerate(self.root.downs):
                if child.index == dobj.index:
                    del self.root.downs[i]
                    break
            for rel, child in self.root.downs:
                if rel == 'dobj':
                    continue
                reassign_parent(child, dobj)
            reassign_parent(self.root, dobj)
            dobj.tag = 'VB'
            dobj.up = 'ROOT', None
            self.root = dobj
            compound = None
            for i, (rel, child) in enumerate(self.root.downs):
                if rel == 'compound':
                    self.root.downs[i] = 'nsubj', child
                    compound = child
                    break
            for i, (rel, child) in enumerate(self.root.downs):
                if rel == 'det':
                    del self.root.downs[i]
                    if compound:
                        compound.downs.append((rel, child))
                        compound.downs.sort(
                            key=lambda (dep, child): child.index)
                    break

            break

        # Sometimes when there's a stranded preposition at the end, the ending
        # punctuation is made its child.  Annoying.
        #
        #   "What is the bedroom east of?"
        while True:
            if not self.tokens:
                break

            t = self.tokens[-1]
            if t.tag != '.':
                break

            rel, orig_parent = t.up
            if rel == 'punct':
                break

            prev_parent = None
            parent = orig_parent
            while parent:
                prev_parent = parent
                _, parent = parent.up
            top_verb = prev_parent

            for i, (_, child) in enumerate(orig_parent.downs):
                if child.index == t.index:
                    del orig_parent.downs[i]
                    break
            t.up = ('punct', top_verb)
            top_verb.downs.append(('punct', t))
            top_verb.downs.sort(key=lambda (dep, child): child.index)

            break

        # Sometimes the parser puts the subject under an acomp for whatever
        # reason.
        #
        #   "Is the chocolate bigger than the box?"
        #
        # Got
        #
        #   is -> bigger -> chocolate
        #
        # Want
        #
        #   is -> chocolate
        #   is -> bigger
        for t in self.tokens:
            # We want to transform
            #
            #   verb -acomp-> JJR -nsubj-> anything
            #
            # into
            #
            #   verb -nsubj-> anything
            #   verb -acomp-> JJR
            rel, parent = t.up
            if rel != 'nsubj':
                continue
            if parent is None:
                continue
            if parent.tag != 'JJR':
                continue
            parent_rel, grandparent = parent.up
            if grandparent is None:
                continue
            if parent_rel != 'acomp':
                continue
            if not grandparent.tag.startswith('V'):
                continue

            # Tree surgery.
            for i, (_, child) in enumerate(parent.downs):
                if child.index == t.index:
                    del parent.downs[i]
                    break
            t.up = (rel, grandparent)
            grandparent.downs.append((rel, t))
            grandparent.downs.sort(key=lambda (dep, child): child.index)

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

        # Usually, preps don't descend from other preps.  If spacy gives us
        # that, attach the child prep to its grandparent instead.
        for t in self.tokens:
            # Transform
            #
            #   verb -prep-> IN-1 -prep-> IN-2
            #
            # into
            #
            #   verb -prep-> IN-1
            #   verb -prep-> IN-2
            if t.tag != 'IN':
                continue
            rel, parent = t.up
            if rel != 'prep':
                continue
            if parent is None:
                continue
            if parent.tag != 'IN':
                continue
            parent_rel, grandparent = parent.up
            if grandparent is None:
                continue
            if parent_rel != 'prep':
                continue

            # Do the surgery.
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


        # If it starts with a "to be" VBZ, it should be of the form
        #
        #   "(is) (something) (something)"
        #
        # so if you get "(is) (something)" try to split the something.
        #
        #   "Is the triangle above the pink rectangle?"
        while True:
            t = self.tokens[0]
            if t.tag != 'VBZ':
                break

            if self.root.index:
                break

            n = len(self.root.downs)
            if n != 2:  # One for punct, the other for the joined arg.
                break

            rel, child = self.root.downs[0]
            if len(child.downs) < 2:  # det, (amod,) prep
                break

            child_rel, grandchild = child.downs[-1]
            if child_rel != 'prep':
                break

            reassign_parent(grandchild, self.root)

            break

        # Convert from
        #
        #   verb -prep-> IN -npadvmod-> anything
        #
        # to
        #
        #   verb -prep-> IN
        #   verb -nsubj-> anything
        for t in self.tokens:
            rel, parent = t.up
            if not parent:
                continue
            if rel != 'npadvmod':
                continue
            if parent.tag != 'IN':
                continue
            parent_rel, grandparent = parent.up
            if not grandparent:
                continue
            if parent_rel != 'prep':
                continue
            if not grandparent.tag.startswith('V'):
                continue

            t.up = 'nsubj', parent
            reassign_parent(t, grandparent)

        # Prepositional phrase attachment: should be owned by another arg.
        #
        #   "The hallway is south of the bedroom."
        for i in xrange(len(self.tokens) - 1):
            this = self.tokens[i]
            right = self.tokens[i + 1]
            directions = ['north', 'south', 'east', 'west']
            if not (this.text in directions and right.tag == 'IN'):
                continue
            if this.tag != 'NN':
                this.tag = 'NN'

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

        # The parser may give us multiple npadvmod links when what we want is
        # just one npadvmod that compound-links to the "other" one.  In other
        # words:
        #
        # Make
        #
        #   "[Yesterday] [evening] Tim moved to the abyss."
        #
        # parse similar to
        #
        #   "[This evening] Tim moved to the abyss."
        verb2npadvmods = defaultdict(list)
        for t in self.tokens:
            rel, parent = t.up
            if not parent:
                continue
            if rel != 'npadvmod':
                continue
            if not parent.tag.startswith('V'):
                continue
            verb2npadvmods[parent.index].append(t.index)
        for verb_x, npadvmod_xx in verb2npadvmods.iteritems():
            if len(npadvmod_xx) == 1:
                continue
            elif len(npadvmod_xx) != 2:
                assert False
            left_x, right_x = npadvmod_xx
            left = self.tokens[left_x]
            right = self.tokens[right_x]
            left.up = ('compound', left.up[1])
            reassign_parent(left, right)

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
