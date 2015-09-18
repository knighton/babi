import json

from panoptes.ling.verb.verb import SurfaceVerb
from panoptes.ling.verb.verb_manager import VerbManager


def main():
    conj_f = 'panoptes/config/conjugations.csv'
    verb_f = 'data/verbs.json'
    m = VerbManager.from_files(conj_f, verb_f)

    j = {
        'sbj_handling': 'WERE_SBJ',
        'relative_cont': 'NOT_REL',
        'contract_not': True,
        'intrinsics': {
            'polarity': {
                'tf': True,
                'is_contrary': False
            },
            'verb_form': 'FINITE',
            'lemma': 'go',
            'tense': 'PRESENT',
            'aspect': {
                'is_prog': False,
                'is_perf': False
            },
            'is_pro_verb': False,
            'modality': {
                'is_cond': False,
                'flavor': 'IMPERATIVE'
            }
        },
        'split_inf': True,
        'is_split': False,
        'conj': 'S2',
        'voice': 'ACTIVE'
    }
    v_to_say = SurfaceVerb.load(j)

    assert m.say(v_to_say) == ([], ['go'])

    sss = ((), ('go',))
    vv = m.parse(sss)
    assert any(map(lambda v: v.may_match(v_to_say), vv))


if __name__ == '__main__':
    main()
