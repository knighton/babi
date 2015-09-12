from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.base import SurfaceArgument


class CommonArgument(DeepArgument, SurfaceArgument):
    """
    An argument that can pass as both surface and deep structure.
    """
    pass
