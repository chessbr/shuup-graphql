# -*- coding: utf-8 -*-
import graphene
import six
from django.db.models import Prefetch
from django.utils.encoding import force_text
from graphene_django import DjangoObjectType
from shuup.core.models import ProductAttribute, ProductMode, ShopProduct, ShopStatus, get_person_contact
from shuup.core.pricing._context import PricingContext
from shuup.core.shop_provider import get_shop
from shuup.core.utils.prices import convert_taxness

from shuup_graphql.front.types.price import PricefulType

from ._category import CategoryType
from ._product import ProductType
from ._product_media import ProductMediaType
from ._supplier import SupplierType


def get_shop_product_queryset():
    return ShopProduct.objects.select_related(
            "shop", "product", "product__sales_unit", "product__primary_image", "product__primary_image__file"
        ).prefetch_related(
            "product__translations", "product__sales_unit__translations", "suppliers"
        ).prefetch_related(
            Prefetch(
                "product__attributes",
                queryset=ProductAttribute.objects.all().prefetch_related("attribute", "attribute__translations")
            )
        ).filter(
            shop__status=ShopStatus.ENABLED,
            product__deleted=False
        )


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
                        product_id=combination["result_product_pk"],
                        shop=self.shop
                    )
                    variations.append({
                        "shop_product": child_shop_product,
                        "sku_part": combination["sku_part"],
                        "hash": combination["hash"],
                        "combination": {
                            force_text(k): force_text(v) for k, v in six.iteritems(combination["variable_to_value"])
                        }
                    })
                except ShopProduct.DoesNotExist:
                    pass
        else:
            children = get_shop_product_queryset().filter(
                shop=self.shop,
                product__variation_parent=self.product,
                product__mode=ProductMode.VARIATION_CHILD
            )
            for child in children:
                try:
                    variations.append({
                        "shop_product": child,
                        "sku_part": child.product.sku,
                        "hash": None,
                        "combination": None
                    })
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


class ShopProductQuery(object):
    shop_products = graphene.List(ShopProductType, search=graphene.String())

    def resolve_shop_products(self, info, search=None, **kwargs):
        queryset = get_shop_product_queryset().filter(
            product__variation_parent__isnull=True,
            product__mode__in=(
                ProductMode.NORMAL,
                ProductMode.VARIABLE_VARIATION_PARENT,
                ProductMode.SIMPLE_VARIATION_PARENT,
                ProductMode.PACKAGE_PARENT
            )
        )

        # if some shop is returned, then use it in the queryset
        # custom shop providers can return no shop and then
        # all manufactures will be returned, like in marketplace environments
        shop = get_shop(info.context)
        if shop:
            queryset = queryset.filter(shop=shop)

        if search:
            queryset = queryset.filter(product__translations__name__icontains=search)

        return queryset
