from collections import defaultdict
import yaml


CAUSE2EFFECTS = {}
fn = 'panoptes/mind/know/cause_and_effect.yaml'
dd = yaml.load(open(fn))
for d in dd:
    cause = d['cause']
    effects = map(lambda s: s.split(), d['effects'])
    CAUSE2EFFECTS[cause] = effects


GET2CAUSE = {}
GO2CAUSES = defaultdict(list)
for cause, effects in CAUSE2EFFECTS.iteritems():
    for verb, target in effects:
        if verb == 'get':
            GET2CAUSE[target] = cause
        elif verb == 'go':
            GO2CAUSES[target].append(cause)
        else:
            assert False
