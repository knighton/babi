# Support for grammatical number.
#
# Grammatical number shows up in different ways in English with varying levels
# of ambiguity, such as singular/plural, which/what, verb conjugation, etc.

from base import enum


N2 = enum.new('N2 = SING PLUR')


N3 = enum.new('N3 = ZERO SING PLUR')


N5 = enum.new('N5 = ZERO SING DUAL FEW MANY')
