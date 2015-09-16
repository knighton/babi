def annotate_as_pro_verb(s):
    return '[PV]' + s


def annotate_as_aux(s):
    return '[AUX]' + s


def remove_verb_annotations(s):
    return a.replace('[PV]', '').replace('[AUX]', '')
