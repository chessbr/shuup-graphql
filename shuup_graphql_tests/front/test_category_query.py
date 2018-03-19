# -*- coding: utf-8 -*-
import json

import pytest
from django.test import Client
from shuup.core.models import Category, CategoryStatus, CategoryVisibility
from shuup.testing import factories


@pytest.mark.django_db
def test_categories_query():
    query = """
    {
        categories {
            id, name, ordering
        }
    }
    """

    shop = factories.get_default_shop()
    client = Client()

    # no categories
    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["categories"] == []

    cat1 = Category.objects.create(
        name="Cat 1", status=CategoryStatus.VISIBLE, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat2 = Category.objects.create(
        name="Cat 2", status=CategoryStatus.VISIBLE, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat3 = Category.objects.create(
        name="Cat 3", status=CategoryStatus.INVISIBLE, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat4 = Category.objects.create(
        name="Cat 5", status=CategoryStatus.DELETED, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat5 = Category.objects.create(
        name="Cat 6", status=CategoryStatus.VISIBLE, visibility=CategoryVisibility.VISIBLE_TO_LOGGED_IN)

    for cat in [cat1, cat2, cat3, cat4, cat5]:
        cat.shops.add(shop)

    # return categories
    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))

    assert len(data["data"]["categories"]) == 2
    assert data["data"]["categories"][0]["id"] == cat1.id
    assert data["data"]["categories"][0]["name"] == cat1.name
    assert data["data"]["categories"][0]["ordering"] == 0
    assert data["data"]["categories"][1]["id"] == cat2.id
    assert data["data"]["categories"][1]["name"] == cat2.name
    assert data["data"]["categories"][1]["ordering"] == 0

    # when authenticated, return also cat5
    user = factories.create_random_user()
    client.force_login(user)

    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]["categories"]) == 3
    assert data["data"]["categories"][2]["id"] == cat5.id
    assert data["data"]["categories"][2]["name"] == cat5.name
    assert data["data"]["categories"][2]["ordering"] == 0


@pytest.mark.django_db
def test_categories_search():
    query = """
    {
        categories(search: "%s") {
            id, name, ordering
        }
    }
    """

    shop = factories.get_default_shop()
    client = Client()

    cat1 = Category.objects.create(
        name="Cat 1", status=CategoryStatus.VISIBLE, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat2 = Category.objects.create(
        name="Cat 2", status=CategoryStatus.VISIBLE, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat3 = Category.objects.create(
        name="Cat 3", status=CategoryStatus.INVISIBLE, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat4 = Category.objects.create(
        name="Cat 5", status=CategoryStatus.DELETED, visibility=CategoryVisibility.VISIBLE_TO_ALL)
    cat5 = Category.objects.create(
        name="Cat 6", status=CategoryStatus.VISIBLE, visibility=CategoryVisibility.VISIBLE_TO_LOGGED_IN)

    for cat in [cat1, cat2, cat3, cat4, cat5]:
        cat.shops.add(shop)

    response = client.get("/gql/", data={"query": query % "cat 2"})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))

    assert len(data["data"]["categories"]) == 1
    assert data["data"]["categories"][0]["id"] == cat2.id
    assert data["data"]["categories"][0]["name"] == cat2.name
    assert data["data"]["categories"][0]["ordering"] == 0

    response = client.get("/gql/", data={"query": query % "cat"})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))

    assert len(data["data"]["categories"]) == 2
    assert data["data"]["categories"][0]["id"] == cat1.id
    assert data["data"]["categories"][0]["name"] == cat1.name
    assert data["data"]["categories"][1]["id"] == cat2.id
    assert data["data"]["categories"][1]["name"] == cat2.name
