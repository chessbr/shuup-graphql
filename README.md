# shuup-graphql
A Shuup GraphQL API implementation

## Installation

Install the package using pip into your virtualenv with Shuup.

## Configuration

In your `urls.py`:

```python
urlpatterns = [
    # ...
    url(r'^gql/', include('shuup_graphql.urls')),
]
```

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'graphene_django',
    'shuup_graphql'

    # These are the supported basket models
    SHUUP_BASKET_CLASS_SPEC="shuup.core.basket.objects:Basket"
    SHUUP_BASKET_ORDER_CREATOR_SPEC="shuup.core.basket.order_creator:BasketOrderCreator"
    SHUUP_BASKET_STORAGE_CLASS_SPEC="shuup.core.basket.storage:DatabaseBasketStorage"
]
```

## Using

Currently we have two main entrypoints: the **Front** and the **Admin**.

The **Front** schema is used mostly for building applications for final users (usually customers). It will only access the current authenticated user information, such as profile, orders and baskets.

The **Admin** schema is used for building management applications. This will allow the authenticated user to access any data from any user.

The example of usage can be seen in unit tests.

## Extending

To extend schemas or even replace our base ones, you just need to change your settings.

If you want to change the schema for front, replace `FRONT_SCHEMA` settings with your own schema:

```py
SHUUP_GRAPHQL = {
    'FRONT_SCHEMA': "myapp.schemas.front.schema"
}
```

Then you can extend our base `FrontQuery` in your `myapp/schemas/front.py`:

```py
from shuup_graphql.front.queries import FrontQuery


class MyCustomFrontQuery(MyCustomUserQuery, FrontQuery):
    pass

schema = graphene.Schema(query=MyCustomFrontQuery)
```

If you would like to remove some of the queries, then you need to create a complete new query and only add the base queries you want:

```py
from shuup_graphql.front.queries._user import UserQuery
from myapp.schemas.custom_query import MyCustomQuery

class MyCustomFrontQuery(UserQuery, MyCustomQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=MyCustomFrontQuery)
```

This is simply a group of mixin classes. The query used in the schema should contain all the classes you want. To extend the Admin, it is basically the same thing, but you must change the `ADMIN_SCHEMA` settings instead.
