#!/usr/bin/env python3

import asyncio, os 

# TODO : add qualification to a separate field
qualifications = ['assistant', 'manager', 'supervisor', 'gcse', 'degree', 'apprentice', 'clerk', 'master', 'jr', 'senior', 'mid', 'junior', 'grad', 'fullstack', 'graduated', 'graduate']

def retrieve_file(name):
    # getting the real path of this file 
    dir = os.path.dirname(os.path.realpath(__file__))
    work_dir = f'{dir}/data'

    f = open(f'{work_dir}/{name}')
    content = f.read()
    f.close()

    return content

comp_skills_db = retrieve_file('comp_skills.txt').splitlines()
simple_skills_db = retrieve_file('simple_skills.txt').splitlines() + qualifications

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
    # TODO : add frequency analysis
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
        