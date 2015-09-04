from ling.glue.purpose import EndPunctClassifier
from ling.parse.parse import Parse
from ling.surface.clause import Clause
from ling.surface.sentence import Sentence


class VerbExtractor(object):
    """
    Finds and parses verbs.
    """

    def __init__(self, verb_mgr):
        self.verb_mgr = verb_mgr

    def extract_all(self, root_token):
        """
        subtree -> yields (verb span pair, SurfaceVerbs)

        Find and parse all possible verbs at the root of the given parse
        subtree.
        """
        # Find all words that make up the verb.
        tt = [root_token]
        for rel, t in root_token.downs:
            if rel == 'aux':
                tt.append(t)

        # Put them in order.
        tt.sort(key=lambda t: t.index)

        # Group consecutive tokens into contiguous spans of verb words.
        spans = []
        begin = 0
        end = begin
        word_tuples = []
        word_tuple = []
        for token in tt[1:]:
            x = token.index

            # If we're part of the same span, just grow it by one.
            #
            # If we're separate, start a new span.
            if end + 1 == x:
                end = x
                word_tuple.append(token.text)
            else:
                spans.append((begin, end))
                begin = x
                end = x
                word_tuples.append(word_tuple)
                word_tuple = [token.text]
        spans.append((begin, end))
        word_tuples.append(word_tuple)

        # Parse given spans.
        if len(spans) == 1:
            # Try the verb words as "pre" words.  Eg, "Did she?"
            sss = tuple(word_tuples[0]), ()
            vv = self.verb_mgr.parse(sss)
            if vv:
                yield (spans[0], ()), vv

            # Try the verb words as "main" words.  Eg, "She did."
            sss = (), tuple(word_tuples[0])
            vv = self.verb_mgr.parse(sss)
            if vv:
                yield ((), spans[0]), vv
        elif len(spans) == 2:
            # Both spans present.  Eg, "Did she know?"
            sss = tuple(word_tuples)
            vv = self.verb_mgr.parse(sss)
            if vv:
                yield tuple(spans), vv
        else:
            # Should never happen.  That would be an interesting parse indeed.
            # Some kind of parser failure.
            assert False

    def extract(self, root_token, is_root_clause):
        """
        subtree, whether root clause -> yields (verb span pair, SurfaceVerbs)

        Find and parse all possible verbs at the root of the given parse
        subtree, then rule out invalid ones.
        """
        for verb_span_pair, vv in self.extract_all(root_token):
            vv = filter(lambda v: v.can_be_in_root_clause(), vv)
            if vv:
                yield verb_span_pair, vv


class SurfaceRecognizer(object):
    def __init__(self, verb_mgr):
        self.end_punct_clf = EndPunctClassifier()
        self.verb_extractor = VerbExtractor(verb_mgr)

    def recog_clause(self, root_token, is_root_clause):
        """
        root token -> yields Clause
        """
        for verb_span_pair, vv in \
                self.verb_extractor.extract(root_token, is_root_clause):
            XXX

    def recog(self, parse):
        """
        Parse -> yields Sentence
        """
        assert isinstance(parse, Parse)

        assert parse.tokens
        end_punct = self.end_punct_clf.classify(parse.tokens[-1])

        for clause in self.recog_clause(parse.root, is_root_clause):
            yield Sentence(clause, end_punct)
