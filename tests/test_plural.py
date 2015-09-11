from ling.morph.plural import PluralManager


def main():
    d = 'config/plural/'
    cat_f = d + 'categories.yaml'
    rule_f = d + 'rules.txt'
    nonsuffix_f = d + 'nonsuffixable.txt'
    cap_f = d + 'capitalized.txt'
    mgr = PluralManager.from_files(cat_f, rule_f, nonsuffix_f, cap_f)
    assert mgr.to_plural('cat') == 'cats'
    assert mgr.to_plural('box') == 'boxes'
    assert mgr.to_plural('ox') == 'oxen'
    assert mgr.to_plural('ax') == 'axes'
    assert mgr.to_plural('axis') == 'axes'


if __name__ == '__main__':
    main()
