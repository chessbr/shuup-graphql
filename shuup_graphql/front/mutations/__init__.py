# -*- coding: utf-8 -*-
import graphene

from ._basket import BasketMutations
from ._category import CategoryMutations


class FrontMutation(BasketMutations, CategoryMutations, graphene.ObjectType):
    pass


__all__ = ["FrontMutation"]
