#!/usr/bin/env python3

import string
import asyncio
import os 

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

# TODO: optimised way to carry an analysis
# unfortunately using nltk multiplies scraping time by 2 
# initialising lemmatizing being the most time consuming
# Solution: use aioObject to initialise the lemma on class 
# creation than meddle with coroutines
class IndeedNLTK:
    """ Processing description and salary for indeed job offers """

    def analyse(self, offer):
        """
        ::Yield:: offer
        """
        txt = offer.txt
        salary = offer.salary

        if txt is None:
            return

        txt = txt.lower()
        # disabeling lemma drasticaly improves the performance (10 to 15sec per run)
        #sanitised = self._sanitise(txt)
        
        skills = self._extract_skills(txt)
        salary = self._extract_salary(salary)

        # replace values in offer with the new values
        offer = offer._replace(salary=salary)
        offer = offer._replace(skills=skills)

        return offer

    def _extract_skills(self, text):
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

    def _extract_salary(self, salary):
        # i.e.: salary = "£500 - £550 a month" ==> "6000, 6600"

        # unavailable salaries = 0
        # (If you're not able to properly fill an ad page, 
        # I don't want to work for you)
        if salary is None:
            # TODO: try to extract the salary from the description
            return ['0']

        # delete '-', '£' and ','
        salary = salary.replace('-', '').replace('£', '').replace(',', '')
        
        # google : (253 working days or 2080 hours per year)
        for word, multiplier in {'year': 1, 'month': 12, 'week': 52, 'day': 253, 'hour': 2080}.items():
            if word in salary:
                # getting rid of the text 
                salary = salary.replace(word, '').replace('a', '').replace('n', '')
                for value in salary.split():
                    # calculating yearly wage 
                    new_value = str(int(float(value) * multiplier))
                    salary = salary.replace(value, new_value)

        return salary.split()
        