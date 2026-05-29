
from sqlalchemy import Column, Integer, String, ForeignKey
from urllib.parse import quote

from .base import Base


class Identifiers(Base):
    __tablename__ = 'identifiers'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False, default="isbn")
    val = Column(String, nullable=False)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)

    def __init__(self, val, id_type, book):
        super().__init__()
        self.val = val
        self.type = id_type
        self.book = book

    def format_type(self):
        format_type = self.type.lower()
        if format_type == 'amazon':
            return "Amazon"
        elif format_type.startswith("amazon_"):
            return "Amazon.{0}".format(format_type[7:])
        elif format_type == "isbn":
            return "ISBN"
        elif format_type == "doi":
            return "DOI"
        elif format_type == "douban":
            return "Douban"
        elif format_type == "goodreads":
            return "Goodreads"
        elif format_type == "babelio":
            return "Babelio"
        elif format_type == "google":
            return "Google Books"
        elif format_type == "kobo":
            return "Kobo"
        elif format_type == "barnesnoble":
            return "Barnes & Noble"
        elif format_type == "litres":
            return "ЛитРес"
        elif format_type == "issn":
            return "ISSN"
        elif format_type == "isfdb":
            return "ISFDB"
        if format_type == "lubimyczytac":
            return "Lubimyczytac"
        if format_type == "databazeknih":
            return "Databáze knih"
        else:
            return self.type

    def __repr__(self):
        format_type = self.type.lower()
        if format_type == "amazon" or format_type == "asin":
            return "https://amazon.com/dp/{0}".format(self.val)
        elif format_type.startswith('amazon_'):
            return "https://amazon.{0}/dp/{1}".format(format_type[7:], self.val)
        elif format_type == "isbn":
            return "https://www.worldcat.org/isbn/{0}".format(self.val)
        elif format_type == "doi":
            return "https://dx.doi.org/{0}".format(self.val)
        elif format_type == "goodreads":
            return "https://www.goodreads.com/book/show/{0}".format(self.val)
        elif format_type == "babelio":
            return "https://www.babelio.com/livres/titre/{0}".format(self.val)
        elif format_type == "douban":
            return "https://book.douban.com/subject/{0}".format(self.val)
        elif format_type == "google":
            return "https://books.google.com/books?id={0}".format(self.val)
        elif format_type == "kobo":
            return "https://www.kobo.com/ebook/{0}".format(self.val)
        elif format_type == "barnesnoble":
            return "https://www.barnesandnoble.com/w/{0}".format(self.val)
        elif format_type == "lubimyczytac":
            return "https://lubimyczytac.pl/ksiazka/{0}/ksiazka".format(self.val)
        elif format_type == "litres":
            return "https://www.litres.ru/{0}".format(self.val)
        elif format_type == "issn":
            return "https://portal.issn.org/resource/ISSN/{0}".format(self.val)
        elif format_type == "isfdb":
            return "http://www.isfdb.org/cgi-bin/pl.cgi?{0}".format(self.val)
        elif format_type == "databazeknih":
            return "https://www.databazeknih.cz/knihy/{0}".format(self.val)
        elif self.val.lower().startswith("javascript:"):
            return quote(self.val)
        elif self.val.lower().startswith("data:"):
            link, __, __ = str.partition(self.val, ",")
            return link
        else:
            return "{0}".format(self.val)

