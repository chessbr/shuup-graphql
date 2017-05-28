# -*- coding: utf-8 -*-
import json

import pytest
from django.test import Client
from shuup.core.models import Manufacturer
from shuup.testing import factories


@pytest.mark.django_db
def test_manufacturer_query():
    query = """
    {
        manufactures {
            id, name, url
        }
    }
    """

    shop = factories.get_default_shop()
    client = Client()

    # no manufacturer
    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["manufactures"] == []

    Manufacturer.objects.create(name="Manuf 1", url="http://www.manuf1.com")
    manuf2 = Manufacturer.objects.create(name="Manuf 2", url="http://www.manuf2.com")
    manuf3 = Manufacturer.objects.create(name="Manuf 3", url="http://www.manuf3.com")

    for manuf in [manuf2, manuf3]:
        manuf.shops.add(shop)

    # get all
    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))

    assert len(data["data"]["manufactures"]) == 2

    assert data["data"]["manufactures"][0]["id"] == manuf2.id
    assert data["data"]["manufactures"][0]["name"] == manuf2.name
    assert data["data"]["manufactures"][0]["url"] == manuf2.url

    assert data["data"]["manufactures"][1]["id"] == manuf3.id
    assert data["data"]["manufactures"][1]["name"] == manuf3.name
    assert data["data"]["manufactures"][1]["url"] == manuf3.url


@pytest.mark.django_db
def test_manufacturer_search():
    query = """
    {
        manufactures (search: "%s") {
            id, name, url
        }
    }
    """

    shop = factories.get_default_shop()
    client = Client()

    Manufacturer.objects.create(name="Manuf 1", url="http://www.manuf1.com")
    manuf2 = Manufacturer.objects.create(name="Manuf 2", url="http://www.manuf2.com")
    manuf3 = Manufacturer.objects.create(name="Manuf 3", url="http://www.manuf3.com")

    for manuf in [manuf2, manuf3]:
        manuf.shops.add(shop)

    # search for
    response = client.get("/gql/", data={"query": query % "manuf 3"})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))

    assert len(data["data"]["manufactures"]) == 1
    assert data["data"]["manufactures"][0]["id"] == manuf3.id
    assert data["data"]["manufactures"][0]["name"] == manuf3.name
    assert data["data"]["manufactures"][0]["url"] == manuf3.url
