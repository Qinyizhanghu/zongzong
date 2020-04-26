from utilities.enum import EnumBase, EnumItem


class CouponTemplateChoices(EnumBase):
    """
    general 普适券
    full 满减券
    """
    GENERAL = EnumItem('ger', u'普适券')
    FULL = EnumItem('full', u'满减券')
