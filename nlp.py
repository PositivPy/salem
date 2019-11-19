#!/usr/bin/env python3

import string
import asyncio
import os 

# TODO : add qualification
qualifications = ['assistant', 'manager', 'supervisor', 'gcse', 'degree', 'apprentice', 'clerk', 'master', 'jr', 'senior', 'mid', 'junior', 'grad', 'fullstack', 'graduated', 'graduate']

dir = os.path.dirname(os.path.realpath(__file__))
dir = f'{dir}/data/'
# TODO : Should probably use a db
f = open(f'{dir}comp_skills.txt')
comp_skills_db = f.read().splitlines()
f.close()

f = open(f'{dir}simple_skills.txt')
simple_skills_db = f.read().splitlines()
f.close()


def analyse(offer):
    """
    ::Yield:: offer
    """
    txt = offer.txt

    if txt is None:
        return

    txt = txt.lower()
    
    skills = extract_skills(txt)

    # replace values in offer with the new values
    new_offer = offer._replace(skills=skills)
    return new_offer

def extract_skills(text):
    text = text.lower()
    # get the composite keywords
    composite = [composite for composite in comp_skills_db if composite in text]

    text = text.split()
    # get the simple keywords
    simple = list(set(text).intersection(simple_skills_db))

    # if the found simple keywords are in the composite keywords
    # delete the simple keyword, as it is part of the composite
    comp_str = ' '.join(composite)
    for word in simple:
        if word in comp_str:
            simple.remove(word)

    keywords = simple + composite
        
    return keywords
        