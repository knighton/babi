# A single token for singular indefinite articles "a" and "an".
A_OR_AN = '<A_OR_AN>'


# A single token for apostrophe-s and lone possessive apostrophe.
#
#   "James' cat" -> James <APOS_S> cat
#   "It is James'." -> It is James <APOS_S> .
#   "Tim's cat" -> Tim <APOS_S> cat
POSSESSIVE_MARK = '<APOS_S>'


# We treat certain extremely common adverbs like "here" and "now" like they are
# actually common nouns with a zero preposition.  Makes the deep structure a lot
# saner.
PLACE_PREP = '<PLACE_PREP>'
TIME_PREP = '<TIME_PREP>'
