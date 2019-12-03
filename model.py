from collections import namedtuple

# this defines the exact name of each property of an offer thru the whole software
# the database's columns and dataframe use the same fields automaticaly
# first three fields define the constrain the primary key

fields = 'title company location minSalary maxSalary description url skills matched'

JobOffer = namedtuple('OFFERS', fields, defaults=(0,) * len(fields.split()))

if __name__ == "__main__":
    model_name = JobOffer.__name__
    fields = JobOffer._fields

    table = "CREATE TABLE IF NOT EXISTS %s (%s, PRIMARY KEY (%s))" \
            % (model_name,", ".join(fields), ", ".join(fields[:3]))
    
    print(table)