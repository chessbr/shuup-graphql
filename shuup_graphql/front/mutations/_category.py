from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import graphene
from shuup.core.models import Category, CategoryStatus
from shuup_graphql.front.types.category import CategoryType

from ..utils.filer import filer_image_from_file_path


class CreateCategoryMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        business_segment = graphene.String(required=True)
        shop = graphene.Int(required=True)
        description = graphene.String(required=False)
        parent_category = graphene.Int(required=False)
        image_url = graphene.String(required=False)

    ok = graphene.Boolean()
    error = graphene.String()
    category = graphene.Field(CategoryType)

    def mutate(self, info, name, business_segment, shop, description=None, parent_category=None, image_url=None):
        # request = info.context
        category = Category.objects.create(name=name, description=description, status=CategoryStatus.VISIBLE)
        if image_url:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(image_url).read())
            img_temp.flush()
            image_file_path = img_temp.name
            path = "ProductCategories/Samples/%s" % business_segment.capitalize()
            filer_image = filer_image_from_file_path(image_file_path, path)
            category.image = filer_image
        if parent_category:
            category.parent = parent_category
        category.shops.add(shop)
        category.save()
        return CreateCategoryMutation(ok=True, category=category)


class CategoryMutations(graphene.ObjectType):
    create_category = CreateCategoryMutation.Field()
