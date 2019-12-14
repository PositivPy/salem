# nlp.py # --> analyse.py
All analysis should be conducted here, query and dataframe analysis too
-> Report.calculate_salary_stats()
-> SkillsReport.extract_skills() : Simplified version for SkillsReport to aggregate before plotting
-> nlp.skills_match(offer_skills, cv_skills)
-> extracting skills should be a single function, usable by controller on any text

# views.py #
-> move plotting here
-> web view should include reports (long process)

# controller #
-> parsing query should be one function
-> separate search into multiple function (retrieve, scrape, save, (analyse?))

# OPTIONS #
-> use different CV
-> use different db
-> web/cli
-> report + specific reports 
-> build controller and pass it to relevant view
