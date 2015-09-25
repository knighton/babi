class Idiolect(object):
    """
    Collection of flags that decide amongst variations in how it can say things.
    """

    def __init__(self, archaic_pro_adverbs=False, contractions=True,
                 pedantic_plurals=False, stranding=True, split_infinitive=True,
                 subjunctive_were=True, whom=False):
        # Whether to use 'archaic' pro-adverbs ("come hither" vs "come here").
        self.archaic_pro_adverbs = archaic_pro_adverbs

        # Whether to use contractions.
        self.contractions = contractions

        # Whether to use pedantic plurals ("genies" vs "genii").
        self.pedantic_plurals = pedantic_plurals

        # Whether to split verb infinitives ("to not go" vs "not to go")
        self.split_infinitive = split_infinitive

        # Whether to use the subjunctive ("If I were president" vs "If I was
        # president").
        self.subjunctive_were = subjunctive_were

        # Whether to strand the preposition of a fronted argument ("What are you
        # talking about?" vs "About what are you talking?").
        #
        #   https://en.wikipedia.org/wiki/Preposition_stranding
        self.stranding = stranding

        # Whether to use 'whom' (pedantic), or replace it with 'who' (casual).
        self.whom = whom
