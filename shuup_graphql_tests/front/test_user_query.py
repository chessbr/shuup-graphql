# -*- coding: utf-8 -*-
import json

import pytest
from django.test import Client
from shuup.testing import factories


@pytest.mark.django_db
def test_user_query():
    factories.get_default_shop()

    query = """
    {
        user {
            id, username
        }
    }
    """

    client = Client()
    response = client.get("/gql/", data={"query": query})

    # no user authenticated
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["user"] is None

    # user authenticated
    user = factories.create_random_user()
    client.force_login(user)
    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["user"]["id"] == user.id
    assert data["data"]["user"]["username"] == user.username

    # try to query password
    response = client.get("/gql/", data={"query": "{ user { password } }"})
    assert response.status_code == 400
