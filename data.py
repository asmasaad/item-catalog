from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, University, College, Base

engine = create_engine('sqlite:///universities.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

university1 = University(name="Immam Muhammad Bin Saud ")
session.add(university1)
session.commit()
user1 = User(name="Fahad", email="fahad@gmail.com")
session.add(user1)
session.commit()
colleg1 = College(name="Computer and Information College",
                  department="Computer Science , Information System , Information Managmnet and Information technology"
                  , university=university1, user=user1)
session.add(colleg1)
session.commit()
colleg2 = College(name="Science College ", department="Physics , Mathmatics & Statistics Chemistry and Biology"
                  , university=university1, user=user1)
session.add(colleg2)
session.commit()
colleg3 = College(name="Economics and Administrative Sciences College ",
                  department="Economics , Accounting , Business Administration , Finance and Investment "
                             ", Banking , Insurance and Risk management"
                  , university=university1, user=user1)
session.add(colleg3)
session.commit()
university2 = University(name="Prince Nourah ")

session.add(university2)
session.commit()
user2 = User(name="MANR", email="manar@gmail.com")
session.add(user2)
session.commit()
college_nourah = College(name="Humanities College ", department="Education , Art ,Social Services And Languages",
                         university=university2, user=user2)
session.add(college_nourah)
session.commit()
college_nourah2 = College(name="Medicine College "
                          , department="Health and Rehabilitation Sciences , Pharmacy ,and  Medicine"
                          , university=university2, user=user2)
session.add(college_nourah2)
session.commit()
college_nourah3 = College(name="Sciences College ", department="Physics , Mathmatics & Statistics Chemistry and Biology",
                          university=university2, user=user2)
session.add(college_nourah3)
session.commit()

university3 = University(name="King Saud ")
session.add(university3)
session.commit()
user3 = User(name="Hind", email="Hind@gmail.com")
session.add(user3)
session.commit()
collegSaud1 = College(name="College of Engineering ",
                      department="Civil Engineering , Chemical Engineering,electrical "
                                 "engineering And Mechanical Engineering",
                      university=university3, user=user3)
session.add(collegSaud1)
session.commit()

collegSaud2 = College(name="College of Science ",
                      department="Physics and astronomy ,Zoology ,Plant and "
                                 "microorganisms,Biochemistry engineering And Mechanical Engineering",
                      university=university3, user=user3)
session.add(collegSaud2)
session.commit()
collegSaud3= College(name="College of Computer and Information",
                     department="Computer Science , Information System , Information Managmnet "
                                ", Information technology , Siftware Engineer", university=university3, user=user3)
session.add(collegSaud3)
session.commit()