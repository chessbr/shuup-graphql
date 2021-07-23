# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import Shop

from .address import AddressType


class ShopType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()
    public_name = graphene.String()
    domain = graphene.String()
    contact_address = graphene.Field(AddressType)

    class Meta:
        model = Shop
        only_fields = ("id", "name", "public_name", "domain", "contact_address")

    def resolve_name(self, info, **kwargs):
        return self.name

    def resolve_public_name(self, info, **kwargs):
        return self.public_name
