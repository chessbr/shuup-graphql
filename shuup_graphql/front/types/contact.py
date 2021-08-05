# -*- coding: utf-8 -*-
import graphene
from graphene_django import DjangoObjectType

from shuup.core.models import CompanyContact, Contact, PersonContact

from .user import UserType


class ContactType(DjangoObjectType):
    id = graphene.Int()

    class Meta:
        model = Contact
        only_fields = ["id", "name"]


class PersonContactType(ContactType):
    user = graphene.Field(UserType)

    class Meta:
        model = PersonContact
        only_fields = ["id", "name", "user"]

    def resolve_user(self, info, **kwargs):
        if isinstance(self, PersonContact):
            return self.user


class CompanyContactType(ContactType):
    class Meta:
        model = CompanyContact
        only_fields = ["id", "name"]


class ContactUnionType(graphene.Union):
    class Meta:
        types = [PersonContactType, CompanyContactType, ContactType]

    @classmethod
    def resolve_type(cls, instance, info):
        if isinstance(instance, PersonContact):
            return PersonContactType
        elif isinstance(instance, CompanyContact):
            return CompanyContactType
        return ContactType
