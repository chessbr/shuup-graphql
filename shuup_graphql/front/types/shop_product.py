# -*- coding: utf-8 -*-
import graphene
import six
from django.utils.encoding import force_text
from graphene_django import DjangoObjectType

from shuup.core.models import ProductMode, ShopProduct, get_person_contact
from shuup.core.pricing._context import PricingContext
from shuup.core.utils.prices import convert_taxness
from shuup_graphql.front.utils.shop_product import get_shop_product_queryset

from .category import CategoryType
from .price import PricefulType
from .product import ProductType
from .product_media import ProductMediaType
from .supplier import SupplierType


class ShopProductType(DjangoObjectType):
    id = graphene.Int()
    price_info = graphene.Field(PricefulType)
    product = graphene.Field(ProductType)
    suppliers = graphene.List(SupplierType)
    primary_category = graphene.Field(CategoryType)
    categories = graphene.List(CategoryType)
    primary_image = graphene.Field(ProductMediaType)
    variations = graphene.List(lambda: VariationShopProductType)

    class Meta:
        model = ShopProduct
        exclude_fields = ("shipping_methods", "payment_methods")

    def resolve_price_info(self, info, **kwargs):
        customer = get_person_contact(info.context.user)
        price_context = PricingContext(shop=self.shop, customer=customer)
        price_info = self.product.get_price_info(price_context)
        return convert_taxness(info.context, self.product, price_info, True)

    def resolve_suppliers(self, info, **kwargs):
        return self.suppliers.all()

    def resolve_categories(self, info, **kwargs):
        return self.categories.all_except_deleted()

    def resolve_variations(self, info, **kwargs):
        variations = []

        if self.product.mode == ProductMode.VARIABLE_VARIATION_PARENT:
            combinations = list(self.product.get_all_available_combinations() or [])
            for combination in combinations:
                try:
                    child_shop_product = get_shop_product_queryset().get(
                        product_id=combination["result_product_pk"], shop=self.shop
                    )
                    variations.append(
                        {
                            "shop_product": child_shop_product,
                            "sku_part": combination["sku_part"],
                            "hash": combination["hash"],
                            "combination": {
                                force_text(k): force_text(v) for k, v in six.iteritems(combination["variable_to_value"])
                            },
                        }
                    )
                except ShopProduct.DoesNotExist:
                    pass
        else:
            children = get_shop_product_queryset().filter(
                shop=self.shop, product__variation_parent=self.product, product__mode=ProductMode.VARIATION_CHILD
            )
            for child in children:
                try:
                    variations.append(
                        {"shop_product": child, "sku_part": child.product.sku, "hash": None, "combination": None}
                    )
                except ShopProduct.DoesNotExist:
                    pass

        return variations


class VariationShopProductType(graphene.ObjectType):
    shop_product = graphene.Field(ShopProductType)
    sku_part = graphene.String()
    hash = graphene.String()
    combination = graphene.JSONString()

    def resolve_sku_part(self, info, **kwargs):
        return self.get("sku_part")

    def resolve_hash(self, info, **kwargs):
        return self.get("hash")

    def resolve_combination(self, info, **kwargs):
        return self.get("combination")

    def resolve_shop_product(self, info, **kwargs):
        return self.get("shop_product")
