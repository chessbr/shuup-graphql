# -*- coding: utf-8 -*-
import graphene

from ._category import CategoryQuery
from ._manufacturer import ManufacturerQuery
from ._user import UserQuery
from ._shop_product import ShopProductQuery


class FrontQuery(UserQuery,
                 CategoryQuery,
                 ManufacturerQuery,
                 ShopProductQuery,
                 graphene.ObjectType):
    pass


__all__ = [
    "FrontQuery"
]
