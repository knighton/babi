from ling.parse.parser import Parser as TextToParse
from ling.tree.surface.recog import ParseToSurface


class SurfaceToDeep(object):
    pass


class DeepToSurface(object):
    pass


class SurfaceToText(object):
    pass


class English(object):
    def __init__(self):
        # Text -> deep structure.
        self.text_to_parse = TextToParse()
        self.parse_to_surface = ParseToSurface()
        self.surface_to_deep = SurfaceToDeep()

        # Deep structure -> text.
        self.deep_to_surface = DeepToSurface()
        self.surface_to_text = SurfaceToText()

    def each_dsen_from_text(self, text):
        print '--Agent.put--'
        for parse in self.text_to_parse.parse(text):
            print '>', parse.dump()
            for surf in self.parse_to_surface.recog(parse):
                print '>>', surf

    def text_from_dsen(self, dsen):
        assert False  # XXX


class Agent(object):
    def __init__(self):
        self.en = English()

    def put(self, text):
        for dsen in self.en.each_dsen_from_text(text):
            print '[[', dsen
