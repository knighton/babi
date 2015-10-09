class Node(object):
    def __init__(self, name):
        self.name = name
        self.links = []

    def dump(self):
        return {
            'name': self.name,
            'links': self.links,
        }

    def add_link(self, direction, name):
        self.links.append((direction, name))


class Graph(object):
    def __init__(self):
        self.x2node = {}
        self.direction2inverse = {
            'is_north_of': 'is_south_of',
            'is_south_of': 'is_north_of',
            'is_east_of': 'is_west_of',
            'is_west_of': 'is_east_of',

            'is_smaller_than': 'is_bigger_than',
            'is_bigger_than': 'is_smaller_than',

            'is_above': 'is_below',
            'is_below': 'is_above',
            'is_left_of': 'is_right_of',
            'is_right_of': 'is_left_of',
            'is_in_front_of': 'is_behind',
            'is_behind': 'is_in_front_of',
        }

    def dump(self):
        x2node = {}
        for x, node in self.x2node.iteritems():
            x2node[x] = node.dump()
        return {
            'x2node': x2node,
        }

    def get(self, name):
        n = self.x2node.get(name)
        if n:
            return n

        self.x2node[name] = Node(name)
        return self.x2node[name]

    def link(self, from_x, direction, to_x):
        assert direction in self.direction2inverse
        from_node = self.get(from_x)
        from_node.add_link(direction, to_x)
        inverse_direction = self.direction2inverse[direction]
        to_node = self.get(to_x)
        to_node.add_link(inverse_direction, from_x)

    def look_toward_direction(self, from_x, direction):
        direction = self.direction2inverse[direction]
        node = self.get(from_x)
        rr = []
        for link_direction, to_x in node.links:
            if link_direction == direction:
                rr.append(to_x)
        return rr

    def look_from_direction(self, from_x, direction):
        assert direction in self.direction2inverse
        node = self.get(from_x)
        rr = []
        for link_direction, to_x in node.links:
            if link_direction == direction:
                rr.append(to_x)
        return rr

    def sub_decide_path(self, from_x, to_x, visited):
        if from_x == to_x:
            return []

        node = self.get(from_x)
        best_path = None
        for direction, next_x in node.links:
            if next_x in visited:
                continue
            path = self.sub_decide_path(
                next_x, to_x, visited + [from_x])
            if path is None:
                continue
            path = [direction] + path
            if best_path is None or len(path) < len(best_path):
                best_path = path
        return best_path

    def shortest_path(self, from_x, to_x):
        return self.sub_decide_path(from_x, to_x, [])

    def sub_each_path(self, from_x, to_x, visited):
        if from_x == to_x:
            yield visited + []

        node = self.get(from_x)
        for direction, next_x in node.links:
            if next_x in visited:
                continue
            for path in self.sub_each_path(next_x, to_x, visited + [from_x]):
                yield [direction] + path

    def each_path(self, from_x, to_x):
        for path in self.sub_each_path(from_x, to_x, []):
            yield path

    def is_direction(self, from_x, direction, to_x):
        for path in self.each_path(from_x, to_x):
            if not path:
                return 'same_thing'

            rels = set(path)
            opposite = self.direction2inverse[direction]
            if direction in rels:
                if opposite in rels:
                    continue
                else:
                    r = 'yes'
            else:
                r = 'no'
            return r
        return 'no'
