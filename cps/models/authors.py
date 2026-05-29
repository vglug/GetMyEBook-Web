from .base import Base
from sqlalchemy import Column, Integer, String


class Authors(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    sort = Column(String)
    link = Column(String, nullable=False, default="")
    image = Column(String, nullable=False, default="")

    def __init__(self, name, sort, link="", image=""):
        super().__init__()
        self.name = name
        self.sort = sort
        self.link = link
        self.image = image

    def get(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def __repr__(self):
        return "<Authors('{0},{1}{2}{3}')>".format(self.name, self.sort, self.link, self.image)
