from sqlalchemy import Column, Integer, String
from .base import Base

class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def get(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def __repr__(self):
        return "<Tags('{0})>".format(self.name)