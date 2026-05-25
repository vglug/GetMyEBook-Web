from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base

class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False, unique=True)
    text = Column(String, nullable=False)

    def __init__(self, comment, book):
        super().__init__()
        self.text = comment
        self.book = book

    def get(self):
        return self.text

    def __repr__(self):
        return "<Comments({0})>".format(self.text)