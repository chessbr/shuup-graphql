# -*- coding: utf-8 -*-
import graphene

from .queries import FrontQuery

schema = graphene.Schema(query=FrontQuery)
