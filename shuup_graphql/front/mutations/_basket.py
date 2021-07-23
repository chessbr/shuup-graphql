# -*- coding: utf-8 -*-
import graphene
from django.core.exceptions import ValidationError
from graphql import GraphQLError
from uuid import uuid4

from shuup.core.basket import get_basket_command_dispatcher
from shuup.core.models import AnonymousContact, Contact, get_company_contact, get_person_contact
from shuup.utils.importing import cached_load
from shuup_graphql.front.types.basket import BasketType


def _handle_cmd(request, command, kwargs):
    try:
        cmd_dispatcher = get_basket_command_dispatcher(request)
        cmd_handler = cmd_dispatcher.get_command_handler(command)
        cmd_kwargs = cmd_dispatcher.preprocess_kwargs(command, kwargs)
        response = cmd_handler(**cmd_kwargs)
        return cmd_dispatcher.postprocess_response(command, cmd_kwargs, response)
    except ValidationError as exc:
        raise GraphQLError(exc.message)


def handle_set_basket_customer(request, basket, customer, orderer=None):
    _handle_cmd(
        request,
        "set_customer",
        {"request": request, "basket": basket, "customer": customer or AnonymousContact(), "orderer": orderer},
    )


class CreateBasketMutation(graphene.Mutation):
    class Arguments:
        customer = graphene.Int(required=False)
        orderer = graphene.Int(required=False)

    ok = graphene.Boolean()
    error = graphene.String()
    basket = graphene.Field(BasketType)

    def mutate(self, info, customer=None, orderer=None):
        request = info.context
        basket_class = cached_load("SHUUP_BASKET_CLASS_SPEC")
        basket = basket_class(info.context, basket_name=uuid4().hex)

        if customer:
            customer = Contact.objects.filter(id=customer).first()
        if orderer:
            orderer = Contact.objects.filter(id=orderer).first()

        if not customer:
            customer = get_company_contact(request.user) or get_person_contact(request.user)
        if not orderer:
            orderer = get_person_contact(request.user)

        handle_set_basket_customer(request, basket, customer, orderer)
        basket.save()

        return CreateBasketMutation(ok=True, basket=basket)


class BasketMutations(graphene.ObjectType):
    create_basket = CreateBasketMutation.Field()
