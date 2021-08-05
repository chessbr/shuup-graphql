# -*- coding: utf-8 -*-
import graphene

from .queries import AdminQuery

# from .mutations import AdminMutation

schema = graphene.Schema(query=AdminQuery)
