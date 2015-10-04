from panoptes.ling.morph.numeral.cardinal import CardinalManager


def main():
    m = CardinalManager()

    fn = 'tests/numeral.txt'
    with open(fn) as f:
        for line in f:
            ss = line.split()
            n = int(ss[0])
            words = ss[1:]
            new_words = m.say_as_words(n)
            assert words == new_words
            new_nn = m.parse(words)
            new_n, = new_nn
            assert n == new_n


if __name__ == '__main__':
    main()
