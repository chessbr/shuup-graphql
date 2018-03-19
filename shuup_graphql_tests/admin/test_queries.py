# -*- coding: utf-8 -*-
import json

import pytest
from django.test import Client
from shuup.testing import factories


@pytest.mark.django_db
def test_user_query():
    shop = factories.get_default_shop()

    query = """
    {
        users {
            id, username
        }
    }
    """

    client = Client()
    response = client.get("/gql/admin/", data={"query": query})

    # no user authenticated
    assert response.status_code == 403
    message = response.content.decode("utf-8")
    assert "User not authenticated." not in message

    # user authenticated but not staff
    user = factories.create_random_user()
    client.force_login(user)
    response = client.get("/gql/admin/", data={"query": query})
    assert response.status_code == 403
    message = response.content.decode("utf-8")
    assert "User has not required permission." not in message

    # user staff but not in shop staff member list
    user.is_staff = True
    user.save()
    response = client.get("/gql/admin/", data={"query": query})
    assert response.status_code == 403
    message = response.content.decode("utf-8")
    assert "User has not required permission." not in message

    # all set
    shop.staff_members.add(user)
    response = client.get("/gql/admin/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["users"][0]["id"] == user.id
    assert data["data"]["users"][0]["username"] == user.username
