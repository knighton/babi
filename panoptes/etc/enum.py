class EnumManager(object):
    def __init__(self):
        self.next_id = 1000000
        self.name2ret = {}

    def new(self, class_name, keys, base_classes):
        assert len(list(set(keys))) == len(keys)
        for s in ['to_str', 'from_str', 'values', 'first', 'last', 'is_valid']:
            assert s not in keys

        # Add this check to catch where modules are moved but not all imports
        # are updated, causing enums created in the module to be created twice
        # with different values.
        if class_name in self.name2ret:
            assert False
        self.name2ret[class_name] = None

        values = list(range(self.next_id, self.next_id + len(keys)))
        key2value = dict(list(zip(keys, values)))
        members = dict(key2value)
        members['to_str'] = dict(list(zip(values, keys)))
        members['from_str'] = key2value
        members['values'] = set(values)
        first = self.next_id
        last = self.next_id + len(keys) - 1
        members['first'] = first
        members['last'] = last
        members['is_valid'] = lambda self, k: \
            isinstance(k, int) and first <= k <= last
        klass = type(class_name, base_classes, members)
        self.next_id += len(keys)
        return klass()


_MGR = EnumManager()


def enum(s, base_classes=None):
    """
    '<enum name> = <list of enum values>' -> enum object

    If you provide base classes, they must be new-style (ie, inherit from
    object.
    """
    if not base_classes:
        base_classes = ()
    ss = s.split()
    assert 2 < len(ss)
    assert ss[1] == '='
    return _MGR.new(ss[0], ss[2:], base_classes)
