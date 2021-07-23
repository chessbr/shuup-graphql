# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models._addresses import Address


class AddressType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = Address
