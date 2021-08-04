import factory.fuzzy as fuzzy
import graphene
from django.conf import settings

from shuup.core.models import (
    MediaFile,
    PersonContact,
    Product,
    ProductMedia,
    ProductMediaKind,
    SalesUnit,
    ShopProduct,
    ShopProductVisibility,
    Shop,
)
from shuup.testing.factories import get_default_product_type, get_default_supplier, get_default_tax_class
from shuup_graphql.front.types.product import ProductType

from ..utils.filer import filer_image_from_url


class CreateProductMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        business_segment = graphene.String(required=True)
        shop = graphene.Int(required=True)
        price = graphene.Decimal(required=False)
        description = graphene.String(required=False)
        image_url = graphene.String(required=False)

    ok = graphene.Boolean()
    error = graphene.String()
    product = graphene.Field(ProductType)

    def mutate(self, info, name, business_segment, shop, description=None, price=None, image_url=None):
        # request = info.context
        product = Product.objects.create(
            name=name,
            description=description,
            type=get_default_product_type(),
            tax_class=get_default_tax_class(),
            sales_unit=SalesUnit.objects.first(),
            sku=fuzzy.FuzzyText(length=10).fuzz(),
        )

        if image_url:
            path = "ProductImages/Samples/%s" % business_segment.capitalize()
            filer_image = filer_image_from_url(image_url, path)
            media_file = MediaFile.objects.create(file=filer_image)
            media_file.shops.add(shop)

            media = ProductMedia.objects.create(product=product, kind=ProductMediaKind.IMAGE, file=filer_image)
            media.save()
            media.shops.add(shop)
            product.primary_image = media
            product.save()

        # create the price and round it to the number of decimals of the currency
        shop = Shop.objects.first()
        if not price:
            price = 0
        product_price = shop.create_price(price).as_rounded()

        sp = ShopProduct.objects.create(
            product=product,
            purchasable=True,
            visibility=ShopProductVisibility.ALWAYS_VISIBLE,
            default_price_value=product_price,
            shop=shop,
            shop_primary_image=media,
        )
        sp.categories.set(shop.categories.all())
        sp.suppliers.add(get_default_supplier())
        sp.save()

        # configure prices
        if "shuup.customer_group_pricing" in settings.INSTALLED_APPS:
            from shuup.customer_group_pricing.models import CgpPrice

            CgpPrice.objects.create(
                product=product, price_value=product_price, shop=shop, group=PersonContact.get_default_group()
            )

        return CreateProductMutation(ok=True, product=product)


class ProductMutations(graphene.ObjectType):
    create_product = CreateProductMutation.Field()
