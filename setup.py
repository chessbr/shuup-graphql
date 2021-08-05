# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

requirements = [
    'graphene-django>=2,<3'
]

setup(
    name="shuup_graphql",
    version="0.1.1",
    author="John Yoost",
    author_email="jyoost@gmail.com",
    url="https://github.com/jyoost/shuup-graphql",
    description=("A Shuup GraphQL API implementation."),
    license="Apache 2.0",
    install_requires=requirements,
    packages=find_packages()
)
