from panoptes.ling.tree.base import BaseArgument


class DeepArgument(BaseArgument):
    """
    An argument in deep structure.
    """

    def to_surface(self, idiolect):
        """
        -> SurfaceArgument

        Generate my corresponding surface structure, after applying
        transformations like fronting.
        """
        raise NotImplementedError
