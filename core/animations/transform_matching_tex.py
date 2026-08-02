from core.animations.transform_matching_abstract_base import TransformMatchingAbstractBase


class TransformMatchingTex(TransformMatchingAbstractBase):
    @staticmethod
    def get_mobject_parts(mobject):
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        return getattr(mobject, 'tex_string',
                       getattr(mobject, '_tex_string',
                               str(id(mobject))))
