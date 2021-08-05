# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import Product, ProductMediaKind

from .manufacturer import ManufacturerType
from .product_media import ProductMediaType
from .sales_unit import SalesUnitType


class ProductType(DjangoObjectType):
    id = graphene.Int()

    name = graphene.String()
    description = graphene.String()
    short_description = graphene.String()
    slug = graphene.String()
    keywords = graphene.String()
    status_text = graphene.String()
    variation_name = graphene.String()

    variation_parent = graphene.Field(lambda: ProductType)
    sales_unit = graphene.Field(SalesUnitType)
    images = graphene.List(ProductMediaType)
    files = graphene.List(ProductMediaType)
    primary_image = graphene.Field(ProductMediaType)
    manufacturer = graphene.Field(ManufacturerType)

    class Meta:
        model = Product
        exclude_fields = ("shops",)

    def resolve_images(self, info, **kwargs):
        return self.media.filter(enabled=True, public=True, kind=ProductMediaKind.IMAGE)

    def resolve_files(self, info, **kwargs):
        return self.get_public_media()
