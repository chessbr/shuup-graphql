# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import ProductMedia


class ProductMediaType(DjangoObjectType):
    # TODO: add thumnail url
    id = graphene.Int()
    url = graphene.String()

    class Meta:
        model = ProductMedia
        only_fields = ("id", "url")

    def resolve_url(self, info, **kwargs):
        if self.external_url:
            return self.external_url
        elif self.file:
            return info.context.build_absolute_uri(self.file.url)
