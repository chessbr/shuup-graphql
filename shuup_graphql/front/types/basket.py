# -*- coding: utf-8 -*-
import graphene

from .address import AddressType
from .contact import ContactUnionType
from .shop import ShopType


class BasketType(graphene.ObjectType):
    id = graphene.Int()
    key = graphene.String()
    customer = graphene.Field(ContactUnionType)
    shop = graphene.Field(ShopType)
    billing_address = graphene.Field(AddressType)
    shipping_address = graphene.Field(AddressType)

    def resolve_customer(self, info, **kwargs):
        if self.customer:
            return self.customer
