# -*- coding: utf-8 -*-
import graphene

from shuup_graphql.front.types.user import UserType


class UserQuery(object):
    user = graphene.Field(UserType)

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user and user.is_authenticated():
            return info.context.user
