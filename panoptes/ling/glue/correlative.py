# Correlatives are determiners, articles, quantifiers, and the like.
#
# All common nouns have a correlative, including special shortcuts words that
# map to common nouns.

from etc.enum import enum


# Used by deep common nouns.
DeepCorrelative = enum("""Correlative =
    INDEFINITE
    DEFINITE
    INTERROGATIVE
    PROXIMAL
    DISTAL
    EXISTENTIAL
    ELECTIVE
    UNIVERSAL
    NEGATIVE
    ALTERNATIVE
""")


# Surface common nouns use this correlative because different types of ELECTIVE
# and UNIVERSAL use different determiners/pronouns (eg. "whichever" vs "any")
# and may have different grammatical numbers (eg. "all cats are" but "every cat
# is").
SurfaceCorrelative = enum("""SurfaceCorrelative =
    INDEF
    DEF
    INTR
    PROX
    DIST
    EXIST
    ELECT_ANY
    ELECT_EVER
    UNIV_EVERY
    UNIV_ALL
    NEG
    ALT
""")
