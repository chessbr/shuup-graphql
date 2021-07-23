# -*- coding: utf-8 -*-
import graphene

from ._basket import BasketMutations


class FrontMutation(BasketMutations, graphene.ObjectType):
    pass


__all__ = ["FrontMutation"]
