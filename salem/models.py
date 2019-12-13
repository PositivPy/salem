#!/usr/bin/env python3

import asyncio
from collections import namedtuple

""" Defines the exact name of each property of an offer thru the whole software
 the database's columns and dataframe use the same fields automaticaly
 first three fields define the constrain the primary key """

fields = 'title company location minSalary maxSalary description url skills matched'

JobOffer = namedtuple('OFFERS', fields, defaults=(0,) * len(fields.split()))


class aioObject(object):
    """ Inheriting this class allows you to define an async __init__.
    So you can create objects by doing something like 'await MyClass(params)'
    https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
    """
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass
