# -*- coding: utf-8 -*-
import graphene

from ._basket import BasketMutations
from ._category import CategoryMutations
from ._product import ProductMutations


class FrontMutation(BasketMutations, CategoryMutations, ProductMutations, graphene.ObjectType):
    pass


__all__ = ["FrontMutation"]
