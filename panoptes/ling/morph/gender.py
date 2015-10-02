from panoptes.ling.glue.inflection import Gender


class GenderClassifier(object):
    """
    Works amazingly well.
    """

    def classify(self, s):
        if not s:
            return Gender.MALE

        s = s.lower()
        c = s[-1]
        if c in 'aey':
            return Gender.FEMALE

        return Gender.MALE
