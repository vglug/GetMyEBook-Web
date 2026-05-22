# metadata.db file convert ORM model

from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Index, Integer, LargeBinary, TIMESTAMP, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.sqltypes import NullType

from cps.models.db import Books

Base = declarative_base()
metadata = Base.metadata


class TimestampMixin:
    """Add creation and update timestamp columns suitable for DB migrations.

    Uses server-side CURRENT_TIMESTAMP so the DB populates and updates them
    automatically. Alembic/Flask-Migrate autogenerate will pick these up.
    """
    created_at = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        server_onupdate=text('CURRENT_TIMESTAMP'),
    )


class Annotations(Base):
    __tablename__ = 'annotations'
    __table_args__ = (
        UniqueConstraint('book', 'user_type', 'user', 'format', 'annot_type', 'annot_id'),
        Index('annot_idx', 'book')
    )

    book = mapped_column(Integer, nullable=False)
    format = mapped_column(Text, nullable=False)
    user_type = mapped_column(Text, nullable=False)
    user = mapped_column(Text, nullable=False)
    timestamp = mapped_column(Float, nullable=False)
    annot_id = mapped_column(Text, nullable=False)
    annot_type = mapped_column(Text, nullable=False)
    annot_data = mapped_column(Text, nullable=False)
    searchable_text = mapped_column(Text, nullable=False, server_default=text("''"))
    id = mapped_column(Integer, primary_key=True)


class AnnotationsDirtied(Base):
    __tablename__ = 'annotations_dirtied'

    book = mapped_column(Integer, nullable=False, unique=True)
    id = mapped_column(Integer, primary_key=True)


t_annotations_fts = Table(
    'annotations_fts', metadata,
    Column('searchable_text', NullType)
)


class AnnotationsFtsConfig(Base):
    __tablename__ = 'annotations_fts_config'

    k = mapped_column(NullType, primary_key=True)
    v = mapped_column(NullType)


class AnnotationsFtsData(Base):
    __tablename__ = 'annotations_fts_data'

    id = mapped_column(Integer, primary_key=True)
    block = mapped_column(LargeBinary)


class AnnotationsFtsDocsize(Base):
    __tablename__ = 'annotations_fts_docsize'

    id = mapped_column(Integer, primary_key=True)
    sz = mapped_column(LargeBinary)


class AnnotationsFtsIdx(Base):
    __tablename__ = 'annotations_fts_idx'

    segid = mapped_column(NullType, primary_key=True, nullable=False)
    term = mapped_column(NullType, primary_key=True, nullable=False)
    pgno = mapped_column(NullType)


t_annotations_fts_stemmed = Table(
    'annotations_fts_stemmed', metadata,
    Column('searchable_text', NullType)
)


class AnnotationsFtsStemmedConfig(Base):
    __tablename__ = 'annotations_fts_stemmed_config'

    k = mapped_column(NullType, primary_key=True)
    v = mapped_column(NullType)


class AnnotationsFtsStemmedData(Base):
    __tablename__ = 'annotations_fts_stemmed_data'

    id = mapped_column(Integer, primary_key=True)
    block = mapped_column(LargeBinary)


class AnnotationsFtsStemmedDocsize(Base):
    __tablename__ = 'annotations_fts_stemmed_docsize'

    id = mapped_column(Integer, primary_key=True)
    sz = mapped_column(LargeBinary)


class AnnotationsFtsStemmedIdx(Base):
    __tablename__ = 'annotations_fts_stemmed_idx'

    segid = mapped_column(NullType, primary_key=True, nullable=False)
    term = mapped_column(NullType, primary_key=True, nullable=False)
    pgno = mapped_column(NullType)

class BooksAuthorsLink(Base):
    __tablename__ = 'books_authors_link'
    __table_args__ = (
        UniqueConstraint('book', 'author'),
        Index('books_authors_link_aidx', 'author'),
        Index('books_authors_link_bidx', 'book')
    )

    book = mapped_column(Integer, nullable=False)
    author = mapped_column(Integer, nullable=False)
    id = mapped_column(Integer, primary_key=True)


class BooksLanguagesLink(Base):
    __tablename__ = 'books_languages_link'
    __table_args__ = (
        UniqueConstraint('book', 'lang_code'),
        Index('books_languages_link_aidx', 'lang_code'),
        Index('books_languages_link_bidx', 'book')
    )

    book = mapped_column(Integer, nullable=False)
    lang_code = mapped_column(Integer, nullable=False)
    item_order = mapped_column(Integer, nullable=False, server_default=text('0'))
    id = mapped_column(Integer, primary_key=True)


class BooksPluginData(Base):
    __tablename__ = 'books_plugin_data'
    __table_args__ = (
        UniqueConstraint('book', 'name'),
    )

    book = mapped_column(Integer, nullable=False)
    name = mapped_column(Text, nullable=False)
    val = mapped_column(Text, nullable=False)
    id = mapped_column(Integer, primary_key=True)


class BooksPublishersLink(Base):
    __tablename__ = 'books_publishers_link'
    __table_args__ = (
        Index('books_publishers_link_aidx', 'publisher'),
        Index('books_publishers_link_bidx', 'book')
    )

    book = mapped_column(Integer, nullable=False, unique=True)
    publisher = mapped_column(Integer, nullable=False)
    id = mapped_column(Integer, primary_key=True)


class BooksRatingsLink(Base):
    __tablename__ = 'books_ratings_link'
    __table_args__ = (
        UniqueConstraint('book', 'rating'),
        Index('books_ratings_link_aidx', 'rating'),
        Index('books_ratings_link_bidx', 'book')
    )

    book = mapped_column(Integer, nullable=False)
    rating = mapped_column(Integer, nullable=False)
    id = mapped_column(Integer, primary_key=True)


class BooksSeriesLink(Base):
    __tablename__ = 'books_series_link'
    __table_args__ = (
        Index('books_series_link_aidx', 'series'),
        Index('books_series_link_bidx', 'book')
    )

    book = mapped_column(Integer, nullable=False, unique=True)
    series = mapped_column(Integer, nullable=False)
    id = mapped_column(Integer, primary_key=True)


class BooksTagsLink(Base):
    __tablename__ = 'books_tags_link'
    __table_args__ = (
        UniqueConstraint('book', 'tag'),
        Index('books_tags_link_aidx', 'tag'),
        Index('books_tags_link_bidx', 'book')
    )

    book = mapped_column(Integer, nullable=False)
    tag = mapped_column(Integer, nullable=False)
    id = mapped_column(Integer, primary_key=True)

class ConversionOptions(TimestampMixin, Base):
    __tablename__ = 'conversion_options'
    __table_args__ = (
        UniqueConstraint('format', 'book'),
        Index('conversion_options_idx_a', 'format'),
        Index('conversion_options_idx_b', 'book')
    )

    format = mapped_column(Text, nullable=False)
    data = mapped_column(LargeBinary, nullable=False)
    id = mapped_column(Integer, primary_key=True)
    book = mapped_column(Integer)

class Feeds(Base):
    __tablename__ = 'feeds'

    title = mapped_column(Text, nullable=False, unique=True)
    script = mapped_column(Text, nullable=False)
    id = mapped_column(Integer, primary_key=True)


class LastReadPositions(Base):
    __tablename__ = 'last_read_positions'
    __table_args__ = (
        UniqueConstraint('user', 'device', 'book', 'format'),
        Index('lrp_idx', 'book')
    )

    book = mapped_column(Integer, nullable=False)
    format = mapped_column(Text, nullable=False)
    user = mapped_column(Text, nullable=False)
    device = mapped_column(Text, nullable=False)
    cfi = mapped_column(Text, nullable=False)
    epoch = mapped_column(Float, nullable=False)
    pos_frac = mapped_column(Float, nullable=False, server_default=text('0'))
    id = mapped_column(Integer, primary_key=True)

class Preferences(TimestampMixin, Base):
    __tablename__ = 'preferences'

    key = mapped_column(Text, nullable=False, unique=True)
    val = mapped_column(Text, nullable=False)
    id = mapped_column(Integer, primary_key=True)

class BooksPagesLink(Books):
    __tablename__ = 'books_pages_link'
    __table_args__ = (
        Index('books_pages_link_pidx', 'needs_scan'),
    )

    pages = mapped_column(Integer, nullable=False, server_default=text('0'))
    algorithm = mapped_column(Integer, nullable=False, server_default=text('0'))
    format = mapped_column(Text, nullable=False, server_default=text("''"))
    format_size = mapped_column(Integer, nullable=False, server_default=text('0'))
    needs_scan = mapped_column(Boolean, nullable=False, server_default=text('0'))
    book = mapped_column(ForeignKey('books.id', ondelete='CASCADE'), primary_key=True)
    timestamp = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
