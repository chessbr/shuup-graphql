# -*- coding: utf-8 -*-
import json

import pytest
from django.test import Client
from shuup.testing import factories


@pytest.mark.django_db
def test_basket_create():
    query = """
    mutation NewBasket {
        createBasket (customer: 0, orderer: 0) {
            ok
            basket {
                key,
                shop { id, name },
                customer {
                    ... on PersonContactType {
                        id
                    }
                }
            }
        }
    }
    """
    shop = factories.get_default_shop()
    client = Client()

    response = client.post("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["createBasket"]["basket"]["key"]
    assert data["data"]["createBasket"]["basket"]["shop"]["id"] == shop.id
    assert data["data"]["createBasket"]["basket"]["shop"]["name"] == shop.name
    assert data["data"]["createBasket"]["ok"] is True


@pytest.mark.django_db
def test_basket_create_with_customer():
    shop = factories.get_default_shop()
    user = factories.create_random_user("en")
    customer = factories.create_random_person()
    customer.user = user
    customer.save()
    customer.shops.add(shop)

    query = """
    mutation NewBasket {
        createBasket (customer: %d, orderer: 0) {
            ok
            basket {
                key,
                customer {
                    ... on PersonContactType {
                        id,
                        name,
                        user { id, username }
                    }
                }
            }
        }
    }
    """
    client = Client()
    client.force_login(user)

    response = client.post("/gql/", data={"query": query % customer.id})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["createBasket"]["ok"] is True
    assert data["data"]["createBasket"]["basket"]["key"]
    assert data["data"]["createBasket"]["basket"]["customer"]["id"] == customer.id
    assert data["data"]["createBasket"]["basket"]["customer"]["name"] == customer.name
    assert data["data"]["createBasket"]["basket"]["customer"]["user"]["id"] == user.id
    assert data["data"]["createBasket"]["basket"]["customer"]["user"]["username"] == user.username
