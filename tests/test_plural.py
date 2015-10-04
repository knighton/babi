from panoptes.ling.morph.plural import PluralManager


def main():
    mgr = PluralManager.default()
    assert mgr.to_plural('cat') == 'cats'
    assert mgr.to_plural('box') == 'boxes'
    assert mgr.to_plural('ox') == 'oxen'
    assert mgr.to_plural('ax') == 'axes'
    assert mgr.to_plural('axis') == 'axes'


if __name__ == '__main__':
    main()
