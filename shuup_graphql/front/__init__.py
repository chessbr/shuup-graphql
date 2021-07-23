# -*- coding: utf-8 -*-
import graphene

from .queries import FrontQuery
from .mutations import FrontMutation

schema = graphene.Schema(query=FrontQuery, mutation=FrontMutation)
