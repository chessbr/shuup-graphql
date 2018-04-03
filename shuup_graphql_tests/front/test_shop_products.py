# -*- coding: utf-8 -*-
import json
from decimal import Decimal

import pytest
from django.test import Client
from shuup.core.models import AnonymousContact, Category, CategoryStatus, ProductMedia, ProductMediaKind
from shuup.customer_group_pricing.models import CgpDiscount
from shuup.testing import factories


def create_images_for_product(shop, product):
    medias = []
    for _ in range(3):
        product_media = ProductMedia.objects.create(product=product, kind=ProductMediaKind.IMAGE)
        product_media.file = factories.get_random_filer_image()
        product_media.save()
        product_media.shops.add(shop)
        medias.append(product_media)
    return medias


def create_categories(shop):
    Category.objects.create(
        name="Category 1", status=CategoryStatus.VISIBLE, image=factories.get_random_filer_image())
    category2 = Category.objects.create(
        name="Category 2", description="parent", slug="cat-2", status=CategoryStatus.VISIBLE)
    Category.objects.create(
        name="Category 2.1", description="visible", slug="cat-2-1", status=CategoryStatus.VISIBLE, parent=category2)
    Category.objects.create(
        name="Category 2.2", description="invisible", slug="cat-2-2", status=CategoryStatus.INVISIBLE, parent=category2)

    for category in Category.objects.all():
        category.shops.add(shop)


@pytest.mark.parametrize("price_includes_tax,product_price,tax_rate,discount", [
    (True, 20, 0.5, 0),
    (False, 20, 0.5, 0),
    (True, 20, 0, 0),
    (False, 20, 0, 0),
    (True, 20, 0.5, 2.5),
    (False, 20, 0.5, 2.5),
    (True, 20, 0, 9.6),
    (False, 20, 0, 9.6),
])
@pytest.mark.django_db
def test_shop_products_query(price_includes_tax, product_price, tax_rate, discount):
    shop = factories.get_default_shop()
    shop.prices_include_tax = price_includes_tax
    shop.save()

    tax = factories.get_default_tax()
    tax.rate = Decimal(tax_rate)
    tax.save()

    query = """
    {
        shopProducts {
            id,
            product {
                name,
                description,
                slug,
                shortDescription,
                salesUnit {
                    id,
                    name,
                    symbol
                },
                primaryImage {
                    id, url
                },
                images {
                    id,
                    url
                }
            },
            purchasable,
            primaryImage {
                id, url
            },
            priceInfo {
                basePrice,
                price,
                discountAmount,
                discountRate,
                discountPercentage,
                isDiscounted,
                taxfulPrice,
                taxfulBasePrice,
                taxlessPrice,
                taxlessBasePrice,
                taxAmount
            },
            suppliers {
                id, name
            },
            primaryCategory {
                id, name
            },
            categories {
                id, name
            }
        }
    }
    """

    client = Client()
    response = client.get("/gql/", data={"query": query})

    # no product
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["data"]["shopProducts"] == []

    supplier = factories.get_default_supplier()
    product = factories.create_product("p1", shop, supplier=supplier, default_price=product_price)
    product.name = "My Product"
    product.description = "Special product"
    product.save()

    # add 3 images for product
    medias = create_images_for_product(shop, product)
    product.primary_image = medias[1]
    product.save()

    create_categories(shop)
    shop_product = product.get_shop_instance(shop)
    shop_product.shop_primary_image = medias[0]
    shop_product.categories = Category.objects.all()
    shop_product.primary_category = Category.objects.first()
    shop_product.save()

    if discount:
        group = AnonymousContact.get_default_group()
        CgpDiscount.objects.create(product=product, shop=shop, group=group, discount_amount_value=discount)

    # returns something
    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]["shopProducts"]) == 1

    discount_amount = discount * (1 if price_includes_tax else (1 + tax_rate))
    assert data["data"]["shopProducts"][0]["id"] == product.id

    assert data["data"]["shopProducts"][0]["product"]["name"] == product.name
    assert data["data"]["shopProducts"][0]["product"]["description"] == product.description
    assert data["data"]["shopProducts"][0]["product"]["slug"] == product.slug
    assert data["data"]["shopProducts"][0]["product"]["shortDescription"] == product.short_description

    assert data["data"]["shopProducts"][0]["product"]["salesUnit"]["id"] == product.sales_unit.id
    assert data["data"]["shopProducts"][0]["product"]["salesUnit"]["name"] == product.sales_unit.name
    assert data["data"]["shopProducts"][0]["product"]["salesUnit"]["symbol"] == product.sales_unit.symbol

    assert data["data"]["shopProducts"][0]["product"]["primaryImage"]["id"] == medias[1].id
    assert data["data"]["shopProducts"][0]["product"]["primaryImage"]["url"].endswith(medias[1].url)
    assert len(data["data"]["shopProducts"][0]["product"]["images"]) == len(medias)

    assert data["data"]["shopProducts"][0]["purchasable"]
    assert data["data"]["shopProducts"][0]["primaryImage"]["id"] == medias[0].id
    assert data["data"]["shopProducts"][0]["primaryImage"]["url"].endswith(medias[0].url)

    assert data["data"]["shopProducts"][0]["suppliers"][0]["id"] == supplier.id
    assert data["data"]["shopProducts"][0]["suppliers"][0]["name"] == supplier.name

    assert len(data["data"]["shopProducts"][0]["categories"]) == Category.objects.count()
    assert data["data"]["shopProducts"][0]["primaryCategory"]["id"] == Category.objects.first().id

    assert data["data"]["shopProducts"][0]["priceInfo"]["discountAmount"] == discount_amount
    assert data["data"]["shopProducts"][0]["priceInfo"]["discountRate"] == (discount / product_price)

    if price_includes_tax:
        assert data["data"]["shopProducts"][0]["priceInfo"]["basePrice"] == product_price
        assert data["data"]["shopProducts"][0]["priceInfo"]["taxfulPrice"] == product_price - discount
        assert data["data"]["shopProducts"][0]["priceInfo"]["price"] == product_price - discount
    else:
        discounted_base_price = product_price - discount
        taxful_price = product_price * (1 + tax_rate)
        price = discounted_base_price * (1 + tax_rate)
        assert data["data"]["shopProducts"][0]["priceInfo"]["taxfulPrice"] == price
        assert data["data"]["shopProducts"][0]["priceInfo"]["price"] == price
        assert data["data"]["shopProducts"][0]["priceInfo"]["basePrice"] == taxful_price
        assert data["data"]["shopProducts"][0]["priceInfo"]["taxfulBasePrice"] == taxful_price
        assert data["data"]["shopProducts"][0]["priceInfo"]["taxlessPrice"] == discounted_base_price
        assert data["data"]["shopProducts"][0]["priceInfo"]["taxlessBasePrice"] == product_price
        assert data["data"]["shopProducts"][0]["priceInfo"]["taxAmount"] == (discounted_base_price * tax_rate)


@pytest.mark.django_db
def test_shop_products_query_with_simple_variation():
    shop = factories.get_default_shop()

    query = """
    {
        shopProducts {
            id,
            product {
                name
            },
            variations {
                shopProduct {
                    id,
                    product {
                        id,
                        name
                    }
                },
                hash,
                combination,
                skuPart
            }
        }
    }
    """

    client = Client()

    supplier = factories.get_default_supplier()
    parent = factories.create_product("parent", shop, supplier=supplier, name="Parent Product")
    child1 = factories.create_product("child1", shop, supplier=supplier, name="Child 1")
    child2 = factories.create_product("child2", shop, supplier=supplier, name="Child 2")

    child1.link_to_parent(parent)
    child2.link_to_parent(parent)

    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]["shopProducts"]) == 1

    assert data["data"]["shopProducts"][0]["id"] == parent.id
    assert data["data"]["shopProducts"][0]["product"]["name"] == parent.name

    assert len(data["data"]["shopProducts"][0]["variations"]) == 2

    assert data["data"]["shopProducts"][0]["variations"][0]["skuPart"] == child1.sku
    assert data["data"]["shopProducts"][0]["variations"][0]["combination"] is None
    assert data["data"]["shopProducts"][0]["variations"][0]["hash"] is None
    assert data["data"]["shopProducts"][0]["variations"][0]["shopProduct"]["product"]["id"] == child1.id
    assert data["data"]["shopProducts"][0]["variations"][0]["shopProduct"]["product"]["name"] == child1.name

    assert data["data"]["shopProducts"][0]["variations"][1]["skuPart"] == child2.sku
    assert data["data"]["shopProducts"][0]["variations"][1]["combination"] is None
    assert data["data"]["shopProducts"][0]["variations"][1]["hash"] is None
    assert data["data"]["shopProducts"][0]["variations"][1]["shopProduct"]["product"]["id"] == child2.id
    assert data["data"]["shopProducts"][0]["variations"][1]["shopProduct"]["product"]["name"] == child2.name


@pytest.mark.django_db
def test_shop_products_query_with_variable_variation():
    shop = factories.get_default_shop()

    query = """
    {
        shopProducts {
            id,
            product {
                name
            },
            variations {
                shopProduct {
                    id,
                    product {
                        id,
                        name
                    }
                },
                hash,
                combination,
                skuPart
            }
        }
    }
    """

    client = Client()

    supplier = factories.get_default_supplier()
    parent = factories.create_product("parent", shop, supplier=supplier, name="Parent Product")
    child1 = factories.create_product("child1", shop, supplier=supplier, name="Child 1")
    child2 = factories.create_product("child2", shop, supplier=supplier, name="Child 2")

    child1.link_to_parent(parent, {"Color": "red", "Size": "XXL"})
    child2.link_to_parent(parent, {"Color": "blue", "Size": "XXXXXL"})

    response = client.get("/gql/", data={"query": query})
    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]["shopProducts"]) == 1

    assert data["data"]["shopProducts"][0]["id"] == parent.id
    assert data["data"]["shopProducts"][0]["product"]["name"] == parent.name

    assert len(data["data"]["shopProducts"][0]["variations"]) == 2

    assert data["data"]["shopProducts"][0]["variations"][0]["shopProduct"]["product"]["id"] == child1.id
    assert data["data"]["shopProducts"][0]["variations"][0]["shopProduct"]["product"]["name"] == child1.name
    assert data["data"]["shopProducts"][0]["variations"][0]["skuPart"] is not None
    assert data["data"]["shopProducts"][0]["variations"][0]["hash"] is not None
    assert json.loads(
        data["data"]["shopProducts"][0]["variations"][0]["combination"]) == {"Color": "red", "Size": "XXL"}

    assert data["data"]["shopProducts"][0]["variations"][1]["shopProduct"]["product"]["id"] == child2.id
    assert data["data"]["shopProducts"][0]["variations"][1]["shopProduct"]["product"]["name"] == child2.name
    assert data["data"]["shopProducts"][0]["variations"][1]["skuPart"] is not None
    assert data["data"]["shopProducts"][0]["variations"][1]["hash"] is not None
    assert json.loads(
        data["data"]["shopProducts"][0]["variations"][1]["combination"]) == {"Color": "blue", "Size": "XXXXXL"}
