# -*- coding: utf-8 -*-
import graphene

from shuup_graphql.front.types.basket import BasketType


class BasketQuery(object):
    basket = graphene.Field(BasketType)
