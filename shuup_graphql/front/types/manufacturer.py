# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import Manufacturer


class ManufacturerType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = Manufacturer
