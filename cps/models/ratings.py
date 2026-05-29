from sqlalchemy import Column, Integer, CheckConstraint, Text

from .base import Base

class Ratings(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, CheckConstraint('rating>-1 AND rating<11'), unique=True)
    link = Column(Text, default="")

    def __init__(self, rating):
        super().__init__()
        self.rating = rating

    def get(self):
        return self.rating

    def __eq__(self, other):
        return self.rating == other

    def __repr__(self):
        return "<Ratings('{0}')>".format(self.rating)