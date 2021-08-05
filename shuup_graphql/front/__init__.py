# -*- coding: utf-8 -*-
import graphene

from .mutations import FrontMutation
from .queries import FrontQuery

schema = graphene.Schema(query=FrontQuery, mutation=FrontMutation)
