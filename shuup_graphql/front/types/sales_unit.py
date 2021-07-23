# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import SalesUnit


class SalesUnitType(DjangoObjectType):
    id = graphene.Int()
    symbol = graphene.String()
    name = graphene.String()

    class Meta:
        model = SalesUnit
