# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import Supplier


class SupplierType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = Supplier
        only_fields = ("id", "identifier", "name")
