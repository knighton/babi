from panoptes.ling.tree.deep.base import DeepArgument
from panoptes.ling.tree.surface.base import SurfaceArgument


class CommonArgument(DeepArgument, SurfaceArgument):
    """
    An argument that can pass as both surface and deep structure.
    """

    def to_surface(self, deep_state, surface_state, idiolect):
        """
        -> SurfaceArgument

        Since we don't contain any surface-only structure because we are a
        "common" argument, to_surface() just means return ourselves.
        """
        return self
