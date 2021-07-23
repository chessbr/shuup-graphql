# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied
from graphene_django.views import GraphQLView

from shuup.admin.shop_provider import get_shop


class AdminGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            raise PermissionDenied("User not authenticated.")

        has_permission = False

        # super users have access
        if getattr(request.user, "is_superuser", False):
            has_permission = True

        # staff members have access
        elif getattr(request.user, "is_staff", False) and request.user in get_shop(request).staff_members.all():
            has_permission = True

        if not has_permission:
            raise PermissionDenied("User has not required permission.")

        return super(AdminGraphQLView, self).dispatch(request, *args, **kwargs)
