# -*- coding: utf-8 -*-
from filer.models import Image
from graphene_django import DjangoObjectType


class FilerImageType(DjangoObjectType):
    class Meta:
        model = Image
        only_fields = ("url",)
