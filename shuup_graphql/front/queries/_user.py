# -*- coding: utf-8 -*-
import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = get_user_model()
        exclude_fields = ["password"]


class UserQuery(object):
    user = graphene.Field(UserType)

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user and user.is_authenticated():
            return info.context.user
