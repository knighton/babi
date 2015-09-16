class AposOrAposSClassifier(object):
    def classify(self, prev_token):
        if not prev_token:
            return "'s"

        if prev_token[-1].lower() == 's':
            return "'"
        else:
            return "'s"
