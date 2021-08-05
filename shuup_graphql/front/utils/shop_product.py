# -*- coding: utf-8 -*-
from django.db.models import Prefetch

from shuup.core.models import ProductAttribute, ShopProduct, ShopStatus


def get_shop_product_queryset():
    return (
        ShopProduct.objects.select_related(
            "shop", "product", "product__sales_unit", "product__primary_image", "product__primary_image__file"
        )
        .prefetch_related("product__translations", "product__sales_unit__translations", "suppliers")
        .prefetch_related(
            Prefetch(
                "product__attributes",
                queryset=ProductAttribute.objects.all().prefetch_related("attribute", "attribute__translations"),
            )
        )
        .filter(shop__status=ShopStatus.ENABLED, product__deleted=False)
    )
