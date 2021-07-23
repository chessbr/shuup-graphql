# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import Category


class CategoryType(DjangoObjectType):
    id = graphene.Int()
    name = graphene.String()

    class Meta:
        model = Category
