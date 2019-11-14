#!/usr/bin/env python3

import string
import asyncio

qualifications = ['assistant', 'manager', 'supervisor', 'gcse', 'degree', 'apprentice', 'clerk', 'master', 'jr', 'senior', 'mid', 'junior', 'grad', 'fullstack', 'graduated', 'graduate']

# TODO : Should probably use a db
f = open('comp_skills')
comp_skills_db = f.read().splitlines()
f.close()

f = open('skills_')
simple_skills_db = f.read().splitlines()
f.close()

skills_db = comp_skills_db + simple_skills_db + qualifications

# TODO: optimised way to carry a full nltk analysis
# unfortunately using nltk multiplies scraping time by 2 
# initialising lemmatizing being the most time consuming
# maybe run the analysis separately and than add it to the database  
class IndeedNLTK:

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
        # extracting skills
        # unfortunately optimising meant getting rid of list comprehension
        # thus comp_skills are not matched for now
        # TODO : optimised way to extract composite skills 
        text = text.lower().split()
        keywords = set(text).intersection(skills_db)

        return keywords

    def _extract_salary(self, salary):
        # i.e.: salary = "£500 - £550 a month" ==> "6000, 6600"

        # pass unavailable salaries
        if salary is None:
            return ['0']

        # delete '-', '£' and ','
        salary = salary.replace('-', '').replace('£', '').replace(',', '')
        
        # removing timeframe text and calculating yearly wage 
        # google : (253 working days or 2080 hours per year)
        for word, multiplier in {'year': 1, 'month': 12, 'week': 52, 'day': 253, 'hour': 2080}.items():
            if word in salary:
                salary = salary.replace(word, '').replace('a', '').replace('n', '')
                for value in salary.split():
                    new_value = str(int(float(value) * multiplier))
                    salary = salary.replace(value, new_value)

        return salary.split()
        