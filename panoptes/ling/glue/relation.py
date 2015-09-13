# Prepositions and grammatical relations.


text = """
relations:

  - relation: IF
    position: OBLIQUE
    order: -100
    preps:
      - if FINITE_CLAUSE

  - relation: WHEN
    position: OBLIQUE
    order: -100]
    preps:
      - when FINITE_CLAUSE

  - relation: AGENT
    position: SUBJECT
    order: 0
    preps:
      - by NOUN

  - relation: TARGET
    position: DIRECT_OBJECT
    order: 3
    preps:
      - X NOUN

  - relation: TO_RECIPIENT
    position: INDIRECT_OBJECT
    order: 1
    preps:
      - to NOUN

  - relation: FOR_RECIPIENT
    position: INDIRECT_OBJECT
    order: 1
    preps:
      - for NOUN

  - relation: BENEFICIARY
    position: OBLIQUE
    order: 5
    preps:
      - for NOUN

  - relation: TO_LOCATION
    position: OBLIQUE
    order: 5
    preps:
      - to NOUN

  - relation: OF
    position: OBLIQUE
    order: 10
    preps:
      - of NOUN

  - relation: ABOUT
    position: OBLIQUE
    order: 10
    preps:
      - about NOUN

  - relation: AT
    position: OBLIQUE
    order: 30
    preps:
      - at NOUN

  - relation: ON
    position: OBLIQUE
    order: 30
    preps:
      - on NOUN

  - relation: DURING
    position: OBLIQUE
    order: 50
    preps:
      - while FINITE_CLAUSE
      - while PREPLESS_GERUND
      - during NOUN

  - relation: BECAUSE
    position: OBLIQUE
    order: 100
    preps:
      - because_of NOUN
      - because FINITE_CLAUSE
      - since FINITE_CLAUSE
"""
