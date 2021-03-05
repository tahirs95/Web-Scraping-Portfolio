from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from datetime import datetime
from sqlalchemy.sql import func
Base = declarative_base()

CONNECTION_STRING = 'mysql+pymysql://user:password@localhost/db_name?charset=utf8'

# lol


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """

    return create_engine(CONNECTION_STRING)


def create_table(engine):
    Base.metadata.create_all(engine)


class Reviews(Base):
    __tablename__ = "reviewsTable"

    id = Column(Integer, primary_key=True)
    review = Column('review', Text(collation='utf8_general_ci'))
    score = Column('score', Float, default=0)

    # def __init__(self, review, score):
    #     self.review = review
    #     self.score = score


class DuplicatesPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        print(
            "****DuplicatesPipeline: database connected****")

    def process_item(self, item):
        session = self.Session()
        exist_quote = session.query(Reviews).filter_by(
            review=item["review"]).first()
        if exist_quote is not None:  # the current quote exists
            try:
                session.close()
            except Exception as e:
                pass
            print("Duplicate item found")
            return True
        else:
            try:
                session.close()
            except Exception as e:
                print(e)
            return False


class ReviewsPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        print("****ReviewsPipeline: database connected****")

    def process_item(self, item):

        session = self.Session()

        review_class = Reviews()

        review_class.review = item['review']
        review_class.score = item['score']

        try:
            session.add(review_class)
            session.commit()

        except:
            session.rollback()
            # raise

        finally:
            session.close()

        return item
