from panoptes.ling.glue.inflection import Gender


class GenderClassifier(object):
    """
    Works amazingly well.
    """

    def classify(self, ss):
        if not ss:
            return Gender.MALE

        s = ss[-1]
        if not s:
            return Gender.MALE

        s = s.lower()
        c = s[-1]
        if c in 'aey':
            return Gender.FEMALE

        return Gender.MALE
