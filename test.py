import asyncio, collections

import nlp, model 

cv = nlp.retrieve_file('example_cv.txt').lower()

cv_skills = nlp.extract_skills(cv)

def skills_match(offer):
    """ Matches the cv's keywords to the offer's
    100% if all the offer's keywords are matched
    """
    global cv_skills
    new_offer = nlp.analyse(offer)
    offer_skills = new_offer.skills
    if not offer_skills:
        return
    matched_skills = set(offer_skills).intersection(cv_skills)

    on = len(offer_skills)
    mn = len(matched_skills)

    p = int((mn / on) * 100)
    if p > 30 and p != 'N/A':
        print(f'Match: {p}% of {on} skills ({mn}/{len(cv_skills)}) : {matched_skills}')

Offer = collections.namedtuple('JobOffer', 'title company salary location \
                                         type_ date txt url link skills',
                                         defaults=(0,))

if __name__=="__main__":
    async def test():
        db = await model.AsyncDB('jobs.db')
        offers = await db.get_all()
        for offer in offers:
            o = Offer(*offer)
            skills_match(o)
    asyncio.run(test())