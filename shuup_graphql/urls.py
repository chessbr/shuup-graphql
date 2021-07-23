# -*- coding: utf-8 -*-
from django.conf.urls import url
from graphene_django.views import GraphQLView

from shuup_graphql.views import AdminGraphQLView

from .settings import shuup_graphql_settings

urlpatterns = [
    url(
        r"^$",
        GraphQLView.as_view(
            graphiql=True,
            schema=shuup_graphql_settings.FRONT_SCHEMA,
        ),
    ),
    url(
        r"^admin/$",
        AdminGraphQLView.as_view(
            graphiql=True,
            schema=shuup_graphql_settings.ADMIN_SCHEMA,
        ),
    ),
]
