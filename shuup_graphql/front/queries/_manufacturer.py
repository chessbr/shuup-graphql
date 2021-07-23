# -*- coding: utf-8 -*-
import graphene

from shuup.core.models import Manufacturer
from shuup.core.shop_provider import get_shop
from shuup_graphql.front.types.manufacturer import ManufacturerType


class ManufacturerQuery(object):
    manufactures = graphene.List(ManufacturerType, search=graphene.String())

    def resolve_manufactures(self, info, search=None, **kwargs):
        queryset = Manufacturer.objects.all()

        # if some shop is returned, then use it in the queryset
        # custom shop providers can return no shop and then
        # all manufactures will be returned, like in marketplace environments
        shop = get_shop(info.context)
        if shop:
            queryset = queryset.filter(shops=shop)

        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset
