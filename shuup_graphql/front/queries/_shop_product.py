# -*- coding: utf-8 -*-
import graphene

from shuup.core.models import ProductMode
from shuup.core.shop_provider import get_shop
from shuup_graphql.front.types.shop_product import ShopProductType
from shuup_graphql.front.utils.shop_product import get_shop_product_queryset


class ShopProductQuery(object):
    shop_products = graphene.List(ShopProductType, search=graphene.String())

    def resolve_shop_products(self, info, search=None, **kwargs):
        queryset = get_shop_product_queryset().filter(
            product__variation_parent__isnull=True,
            product__mode__in=(
                ProductMode.NORMAL,
                ProductMode.VARIABLE_VARIATION_PARENT,
                ProductMode.SIMPLE_VARIATION_PARENT,
                ProductMode.PACKAGE_PARENT,
            ),
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
