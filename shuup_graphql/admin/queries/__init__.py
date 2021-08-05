# -*- coding: utf-8 -*-
import graphene

from ._users import AdminUsersQuery


class AdminQuery(AdminUsersQuery, graphene.ObjectType):
    pass


__all__ = ["AdminQuery"]
