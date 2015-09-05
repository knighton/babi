from base.enum import enum


# Correlatives are determiners, articles, quantifiers, and the like.
#
# All common nouns have a correlative, including special shortcuts words that
# map to common nouns.
Correlative = enum("""Correlative =
    INDEFINITE
    DEFINITE
    INTERROGATIVE
    PROXIMAL
    DISTAL
    EXISTENTIAL
    ELECTIVE_ANY
    ELECTIVE_EVER
    UNIVERSAL_ALL
    UNIVERSAL_EVERY
    NEGATIVE
    ALTERNATIVE
""")


# Correlative -> whether it's interrogative.
CORRELATIVE2IS_INTERROGATIVE = dict(zip(
    sorted(Correlative.values),
    map(lambda c: c not in (Correlative.INTERROGATIVE,
                            Correlative.ELECTIVE_EVER),
        sorted(Correlative.values))))
