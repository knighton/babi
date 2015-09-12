from panoptes.ling.tree.base import BaseArgument


class DeepArgument(BaseArgument):
    """
    An argument in deep structure.
    """

    def generate(self):
        """
        -> SurfaceArgument

        Generate my corresponding surface structure, after applying
        transformations like fronting.
        """
        raise NotImplementedError
