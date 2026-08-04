from manim import Group, VGroup
from core.animations.transform_matching_abstract_base import TransformMatchingAbstractBase


class TransformMatchingTex(TransformMatchingAbstractBase):
    @staticmethod
    def get_mobject_parts(mobject):
        """Recursively extract MathTexPart leaf submobjects.

        For Groups/VGroups, recurse into each direct child.  For non-group
        mobjects (MathTex), return their submobjects — these are the
        MathTexPart instances with tex_string attributes that serve as
        matching keys.  This matches the original manim behaviour so that
        ``Group(eq1, variables)`` yields the individual parts of eq1
        AND the parts of each MathTex inside variables, not just the
        two top-level items."""
        if isinstance(mobject, (Group, VGroup)):
            parts = []
            for s in mobject.submobjects:
                parts.extend(TransformMatchingTex.get_mobject_parts(s))
            return parts
        # MathTex / SingleStringMathTex: return its MathTexPart submobjects
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        """Return the tex_string that identifies a MathTexPart for matching."""
        return getattr(mobject, 'tex_string',
                       getattr(mobject, '_tex_string',
                               str(id(mobject))))
