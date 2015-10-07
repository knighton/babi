from panoptes.etc.dicts import v2k_from_k2v
from panoptes.etc.enum import enum


Conjunction = enum('Conjunction = ALL_OF ONE_OF')


CONJUNCTION2STR = {
    Conjunction.ALL_OF: 'and',
    Conjunction.ONE_OF: 'or',
}


STR2CONJUNCTION = v2k_from_k2v(CONJUNCTION2STR)
