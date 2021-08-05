# -*- coding: utf-8 -*-
import graphene

from ._category import CategoryQuery
from ._manufacturer import ManufacturerQuery
from ._shop_product import ShopProductQuery
from ._user import UserQuery


class FrontQuery(UserQuery, CategoryQuery, ManufacturerQuery, ShopProductQuery, graphene.ObjectType):
    pass


__all__ = ["FrontQuery"]
