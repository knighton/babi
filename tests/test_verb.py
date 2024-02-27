import json
import yaml

from panoptes.ling.verb.verb import SurfaceVerb
from panoptes.ling.verb.verb_manager import VerbManager


def main():
    conj_f = 'panoptes/ling/verb/conjugations.csv'
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
    assert any([v.may_match(v_to_say) for v in vv])

    text = """
        sbj_handling: WERE_SBJ
        relative_cont: NOT_REL
        contract_not: true
        split_inf: true
        is_split: true
        conj: S2
        voice: ACTIVE
        intrinsics:
            lemma: go
            polarity:
                tf: true
                is_contrary: false
            tense: PRESENT
            aspect:
                is_perf: true
                is_prog: false
            modality:
                flavor: INDICATIVE
                is_cond: true
            verb_form: FINITE
            is_pro_verb: false
    """
    j = yaml.safe_load(text)
    v = SurfaceVerb.load(j)

    assert m.say(v) == (['would'], ['[AUX]have', 'gone'])


if __name__ == '__main__':
    main()
