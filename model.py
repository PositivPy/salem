#!/usr/bin/env python3

from collections import namedtuple

""" Defines the exact name of each property of an offer thru the whole software
 the database's columns and dataframe use the same fields automaticaly
 first three fields define the constrain the primary key """

fields = 'title company location minSalary maxSalary description url skills matched'

JobOffer = namedtuple('OFFERS', fields, defaults=(0,) * len(fields.split()))
