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
    new_parent.downs.sort(key=lambda dep_child9: dep_child9[1].index)


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
        print('INPUT TO FIXED:')
        self.dump()

        # XX tokens, ugh.
        for t in self.tokens:
            if t.tag == 'XX':
                t.tag = 'NNP'
                t.up = ('nsubj', t.up[1])
                reassign_parent(t, t.up[1])

        # Jason is a proper noun.
        for t in self.tokens:
            if t.text in ('jason', 'antoine', 'sumit', 'yann'):
                t.tag = 'NNP'

        # Tokens that descend from sentence-ending punctuation shall be
        # reassigned to the root.
        #
        #   "What is the hallway north of?"
        while True:
            t = self.tokens[-1]
            if t.tag != '.':
                break

            for rel, child in t.downs:
                reassign_parent(child, self.root)

            break

        # "The" is not a direct verb argument.
        #
        #   "What is the hallway north of?"
        #
        # Convert
        #
        #   V* -nsubj-> the
        #
        # to
        #
        #  (token after the) -det-> the
        for t in self.tokens:
            rel, parent = t.up
            if not parent:
                continue
            if not parent.tag.startswith('V'):
                continue
            if rel != 'nsubj':
                continue
            if t.text != 'the':
                continue
            if len(self.tokens) < t.index + 1:
                continue
            next_token = self.tokens[t.index + 1]
            next_rel, next_parent = next_token.up
            if next_rel != 'nmod':
                continue
            next_token.up = 'nsubj', next_parent
            reassign_parent(next_token, next_parent)
            t.up = 'det', parent
            reassign_parent(t, self.tokens[t.index + 1])

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
                            key=lambda dep_child: dep_child[1].index)
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
            top_verb.downs.sort(key=lambda dep_child1: dep_child1[1].index)

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
            grandparent.downs.sort(key=lambda dep_child2: dep_child2[1].index)

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
            grandparent.downs.sort(key=lambda dep_child3: dep_child3[1].index)

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
            grandparent.downs.sort(key=lambda dep_child4: dep_child4[1].index)

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
            grandparent.downs.sort(key=lambda dep_child5: dep_child5[1].index)

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
            t.downs.sort(key=lambda dep_child6: dep_child6[1].index)

        # Possibly the worst hack.
        #
        # Example:
        #
        #   "Is [the box of chocolates] [bigger than the box]?"
        while True:
            t = self.tokens[0]
            if t.tag != 'VBZ':
                break

            if self.root.index:
                break

            n = len(self.root.downs)
            if n != 2:  # One for the joined arg, one for ending punct.
                break

            rel, child = self.root.downs[1]
            if rel != 'punct':
                break

            for t in self.tokens:
                if t.tag == 'JJR' and t.up[0] == 'amod':
                    t.up = ('nsubj', t.up[1])
                    reassign_parent(t, self.root)
            break

        # If it starts with a "to be" VBZ, it should be of the form
        #
        #   "(is) (something) (something)"
        #
        # so if you get "(is) (something)" try to split the something.
        #
        #   "Is the triangle above the pink rectangle?"
        #
        # and
        #
        #   "Is the box bigger than the box of chocolates?"
        #
        # however note this won't handle the following alone:
        #
        #   "Is [the box of chocolates] [bigger than the box]?"
        while True:
            t = self.tokens[0]
            if t.tag != 'VBZ':
                break

            if self.root.index:
                break

            n = len(self.root.downs)
            if n != 2:  # One for punct, the other for the joined arg.
                break

            rel, child = self.root.downs[1]
            if rel != 'punct':
                break

            rel, child = self.root.downs[0]
            if len(child.downs) < 2:  # det, (amod,) prep
                break

            child_rel, grandchild = child.downs[-1]
            if child_rel == 'prep':
                reassign_parent(grandchild, self.root)
            elif child_rel == 'amod':
                child.downs[1] = ('acomp', grandchild)
                grandchild.up = ('acomp', child)
                reassign_parent(grandchild, self.root)
            else:
                break

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
        for i in range(len(self.tokens) - 1):
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
            this.downs.sort(key=lambda rel_child: rel_child[1].index)

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
            grandparent.downs.sort(key=lambda dep_child7: dep_child7[1].index)

        # Handle verb args descended from an aux relation.
        for t in self.tokens:
            dep, up = t.up
            if up is None:
                continue
            up_dep, up_up = up.up
            if up_up is None:
                continue
            if up_dep not in ('aux', 'auxpass'):
                continue
            for i, (_, child) in enumerate(up.downs):
                if child.index == t.index:
                    del up.downs[i]
                    break
            t.up = (dep, up_up)
            up_up.downs.append((dep, t))
            up_up.downs.sort(key=lambda a_b: a_b[1].index)

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
            t.up[1].downs.sort(key=lambda a_b8: a_b8[1].index)

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
        for verb_x, npadvmod_xx in verb2npadvmods.items():
            if len(npadvmod_xx) == 1:
                continue
            elif len(npadvmod_xx) != 2:
                assert False
            left_x, right_x = npadvmod_xx
            left = self.tokens[left_x]
            right = self.tokens[right_x]
            left.up = ('compound', left.up[1])
            reassign_parent(left, right)

        # At least in the bAbi dataset, the same sentence 'shape' almost always
        # parses one way, but in a few cases it parses the other way.  Normalize
        # those to the common way.
        #
        #   "Julie is either in the bedroom or the office." -- canonical
        #   "Mary is either in the school or the office." -- non-canonical
        #
        # Reassign "cc" and "conj" relations descending from an IN token to its
        # "pobj" child.
        for t in self.tokens:
            if t.tag != 'IN':
                continue

            pobj = None
            for rel, child in t.downs:
                if rel == 'pobj':
                    pobj = child
                    break
            if pobj is None:
                continue

            for rel, child in list(t.downs):
                if rel in ('cc', 'conj'):
                    reassign_parent(child, pobj)

        # Convert
        #
        #   V* -*-> NN(s) -advmod-> RB
        #
        # to
        #
        #   V* -*-> NN(s)
        #   V* -advmod-> RB
        for t in self.tokens:
            if t.tag != 'RB':
                continue
            rel, parent = t.up
            if rel != 'advmod':
                continue
            if not parent:
                continue
            if not parent.tag.startswith('N'):
                continue
            parent_rel, grandparent = parent.up
            reassign_parent(t, grandparent)

        return self

    def dump(self):
        print('Parse {')

        print('   ', end=' ')
        for t in self.tokens:
            print('%d=%s/%s' % (t.index, t.text, t.tag), end=' ')
        print()

        def fix(xxx_todo_changeme):
            (rel, parent) = xxx_todo_changeme
            if parent:
                parent = parent.index
            return ' '.join(map(str, [rel, parent]))

        for t in self.tokens:
            print('   ', fix(t.up), '->', t.index, '->', list(map(fix, t.downs)))

        print('}')
