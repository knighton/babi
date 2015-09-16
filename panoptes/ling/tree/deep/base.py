from panoptes.ling.tree.base import BaseArgument


class DeepState(object):
    def __init__(self, arbitrary_say_context, purpose_mgr, relation_mgr):
        self.arbitrary_say_context = arbitrary_say_context  # SayContext
        self.relation_mgr = relation_mgr  # RelationManager
        self.purpose_mgr = purpose_mgr    # PurposeManager


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

    def to_surface(self, deep_state, surface_state, idiolect):
        """
        DeepState, SayState, Idiolect -> SurfaceArgument

        Generate my corresponding surface structure, after applying
        transformations like fronting.

        Deep content clauses need to get conjugation for the verb, which means
        for surface common nouns it needs to partially say it, so we need
        surface state for saying.
        """
        raise NotImplementedError
