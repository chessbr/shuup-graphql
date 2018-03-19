# -*- coding: utf-8 -*-
import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class AdminUserType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = get_user_model()
        exclude_fields = ["password"]


class AdminUsersQuery(object):
    users = graphene.List(AdminUserType)

    def resolve_users(self, info, **kwargs):
        return get_user_model().objects.all()
