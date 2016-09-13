### panoptes (solution for [fb.ai/babi](https://fb.ai/babi) 20 QA tasks)

#### 1. English pipeline

                                                                  |
    +------+     +--------+     +-----------+     +-----------+   |   +--------+
    |      | --> | Parse  | --> |           | --> |           | --|-> |        |
    | Text |     |        |     | Surface   |     | Deep      |   |   | Memory |
    |      |     |        |     | Structure |     | Structure |   |   |        |
    |      | <-- | Tokens | <-- |           | <-- |           | <-|-- |        |
    +------+     +--------+     +-----------+     +-----------+   |   +--------+
              ^              ^                 ^                  |
              |              |                 |                  |
           Parsing/      Recognizing/     Wh-fronting         Reference
           Contractions  Rendering                            Resolution

#### 2. Deep structure examples

##### Where would they have gone?

    root:
        type: DeepContentClause
        status: ACTUAL
        purpose: WH_Q
        is_intense: false
        verb:
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
        rels_vargs:
          -
              - AGENT
              - type: PersonalPronoun
                declension: THEY2
                ppcase: SUBJECT
          -
              - PLACE
              - type: DeepCommonNoun
                possessor:
                selector:
                    correlative: INTR
                    n_min: SING
                    n_max: SING
                    of_n_min: SING
                    of_n_max: SING
                number:
                attributes: []
                noun: place
                rels_nargs: []
        subj_index: 0
