import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dburi = os.environ['PMS_DATABASE_URI']

engine = create_engine(dburi)
Session = sessionmaker(bind=engine)
session = Session()
