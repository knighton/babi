from panoptes.ling.tree.base import BaseArgument


class TransformState(object):
    """
    State required for args to implement to_surface().
    """

    def __init__(self, arbitrary_say_context, purpose_mgr, relation_mgr):
        self.arbitrary_say_context = arbitrary_say_context  # SayContext
        self.relation_mgr = relation_mgr  # RelationManager
        self.purpose_mgr = purpose_mgr    # PurposeManager


class DeepArgument(BaseArgument):
    """
    An argument in deep structure.
    """

    def to_surface(self, transform_state, say_state, idiolect):
        """
        TransformState, SayState, Idiolect -> SurfaceArgument

        Generate my corresponding surface structure, after applying
        transformations like fronting.

        Deep content clauses need to get conjugation for the verb, which means
        for surface common nouns it needs to partially say it, so we need
        surface state for saying.
        """
        raise NotImplementedError
