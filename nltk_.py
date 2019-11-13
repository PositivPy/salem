import nltk
import sys
import string

# living wage is £21,944 a year or 10.55 and hour

qualifications = ['assistant', 'manager', 'supervisor', 'gcse', 'degree', 'apprentice', 'clerk', 'master', 'jr', 'senior', 'mid', 'junior', 'grad', 'fullstack', 'graduated', 'graduate']

# TODO : Should probably use a db
f = open('comp_skills')
comp_skill_db = f.read().splitlines()
f.close()

f = open('skills_')
skill_db = f.read().splitlines()
f.close()


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
        sanitised = self._sanitise(txt)
        skills = self._extract_skills(txt, sanitised)
        salary = self._extract_salary(salary)

        # replace values in offer with the new values
        offer = offer._replace(salary=salary)
        offer = offer._replace(skills=skills)

        return offer

    def _sanitise(self, text):
        """
        Return list of sanitised words; remove punctuation, split, lemmatize, stem
        ::return:: list
        """

        # remove punctuation
        text = text.translate(str.maketrans(' ', ' ', string.punctuation))

        text = text.lower()

        # split text
        tokens = nltk.word_tokenize(text)
        if len(tokens) < 2:
            return

        # singular to plurial
        lemma = nltk.stem.WordNetLemmatizer()
        lem = [lemma.lemmatize(word) for word in tokens]

        # words to word's stem i.e.; programer => program
        stemma = nltk.stem.PorterStemmer()
        stem = [stemma.stem(token) for token in lem]
        
        return stem

    def _extract_skills(self, text, sanitised):
        # TODO : clean this up somehow 
        comp = self._comp_skills(text)
        simple = self._extract_simple_skills(sanitised)
        return simple + comp

    def _comp_skills(self, text):
        # extracting skills
        text = text.lower()
        keywords = [w for w in comp_skill_db if w in text]
        return keywords

        # frequency distribution on keywords 
        tag_fd = dict(nltk.FreqDist(word for word in keywords))
        # as sorted list of tuples
        tag_fd = sorted(tag_fd.items(), key=lambda x: x[1], reverse=True)
        print(tag_fd)
        return tag_fd

    def _extract_simple_skills(self, sanitised):
        keywords = [w for w in skill_db if w in sanitised]

        # frequency distribution on keywords 
        tag_fd = dict(nltk.FreqDist(word for word in keywords))
        # as sorted list of tuples
        tag_fd = sorted(tag_fd.items(), key=lambda x: x[1], reverse=True)
    
        return keywords

    def _extract_salary(self, salary):
        # i.e.: salary = "£500 - £550 a month" ==> "6000, 6600"

        # pass unavailable salaries
        if salary is None:
            return '0'

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
        