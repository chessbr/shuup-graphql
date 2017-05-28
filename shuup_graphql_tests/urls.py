# This file is part of Shuup.
from django.conf.urls import include, url

urlpatterns = [
    url(r'^gql/', include('shuup_graphql.urls')),
]
