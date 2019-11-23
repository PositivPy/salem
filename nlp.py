#!/usr/bin/env python3

import asyncio, os, logging

log = logging.getLogger(__file__)

# TODO : add qualification to a separate field
qualifications = ['intern', 'assistant', 'manager', 'supervisor', 'gcse', 'degree', 'apprentice', 'clerk', 'master', 'jr', 'senior', 'mid', 'junior', 'grad', 'fullstack', 'graduated', 'graduate']

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
cv = retrieve_file('example_cv.txt')

def analyse(offer):
    """
    ::Yield:: offer
    """
    log.debug(f"Analysing offer {offer.title}")
    txt = offer.description
    
    skills = extract_skills(txt)
    matched_skills = skills_match(skills)
    # replace values in offer with the new values
    new_offer = offer._replace(skills=skills)
    new_offer = new_offer._replace(matched=matched_skills)
    return new_offer

def extract_skills(text):
    if text is None:
        return 0
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

cv_skills = extract_skills(cv)

def skills_match(offer_skills):
    """ Matches the cv's keywords to the offer's
    100% if all the offer's keywords are matched
    """
    global cv_skills

    if not offer_skills:
        return 0

    matched_skills = set(offer_skills).intersection(cv_skills)

    on = len(offer_skills)
    mn = len(matched_skills)

    p = int((mn / on) * 100)
    #if p > 30 and p != 'N/A':
    #print(f'Match: {p}% of {on} skills ({mn}/{len(cv_skills)}) : {matched_skills}')
    return p
        