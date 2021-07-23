# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import Category, get_person_contact
from shuup.core.shop_provider import get_shop


class CategoryType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()

    class Meta:
        model = Category


class CategoryQuery(object):
    categories = graphene.List(CategoryType, search=graphene.String())

    def resolve_categories(self, info, search=None, **kwargs):
        # if some shop is returned, then use it in the queryset
        # custom shop providers can return no shop and then
        # all catgories will be returned, like in marketplace environments
        queryset = Category.objects.all_visible(get_person_contact(info.context.user), get_shop(info.context))

        if search:
            queryset = queryset.filter(translations__name__icontains=search)

        return queryset
