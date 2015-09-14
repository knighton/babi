from panoptes.ling.tree.base import BaseArgument


class DeepArgument(BaseArgument):
    """
    An argument in deep structure.
    """

    def relation_arg_type(self):
        """
        -> RelationArgType

        What type of argument are we, as far as relations/prepositions are
        concerned (inert, finite clause, etc.).
        """
        raise NotImplementedError

    def to_surface(self, idiolect):
        """
        -> SurfaceArgument

        Generate my corresponding surface structure, after applying
        transformations like fronting.
        """
        raise NotImplementedError
