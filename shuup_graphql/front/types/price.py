# -*- coding: utf-8 -*-
import graphene
from decimal import Decimal


class PricefulType(graphene.ObjectType):
    base_price = graphene.Float()
    price = graphene.Float()
    discount_amount = graphene.Float()
    discount_rate = graphene.Float()
    discount_percentage = graphene.Float()
    taxful_price = graphene.Float()
    taxless_price = graphene.Float()
    taxful_base_price = graphene.Float()
    taxless_base_price = graphene.Float()
    tax_amount = graphene.Float()
    is_discounted = graphene.Boolean()

    def resolve_base_price(self, info, **kwargs):
        return self.base_price.value

    def resolve_price(self, info, **kwargs):
        return self.price.value

    def resolve_discount_amount(self, info, **kwargs):
        return self.discount_amount.value

    def resolve_taxful_price(self, info, **kwargs):
        return self.taxful_price.value

    def resolve_taxless_price(self, info, **kwargs):
        if hasattr(self, "tax_amount"):
            return self.taxless_price.value
        return Decimal()

    def resolve_taxful_base_price(self, info, **kwargs):
        if hasattr(self, "tax_amount"):
            return self.taxful_base_price.value
        return Decimal()

    def resolve_taxless_base_price(self, info, **kwargs):
        if hasattr(self, "tax_amount"):
            return self.taxless_base_price.value
        return Decimal()

    def resolve_tax_amount(self, info, **kwargs):
        if hasattr(self, "tax_amount"):
            return self.tax_amount.value
        return Decimal()
