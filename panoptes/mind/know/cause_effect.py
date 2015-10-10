import yaml


CAUSE2EFFECTS = {}
fn = 'data/cause_and_effect.yaml'
dd = yaml.load(open(fn))
for d in dd:
    cause = d['cause']
    effects = map(lambda s: s.split(), d['effects'])
    CAUSE2EFFECTS[cause] = effects
