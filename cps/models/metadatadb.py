# metadata.db file convert ORM model

from sqlalchemy import Boolean, Column, Float, ForeignKey, Index, Integer, LargeBinary, TIMESTAMP, Table, Text, UniqueConstraint, text

from .base import Base
from .db import Books
metadata = Base.metadata


class TimestampMixin:
    """Add creation and update timestamp columns suitable for DB migrations.

    Uses server-side CURRENT_TIMESTAMP so the DB populates and updates them
    automatically. Alembic/Flask-Migrate autogenerate will pick these up.
    """
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
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

    book = Column(Integer, nullable=False)
    format = Column(Text, nullable=False)
    user_type = Column(Text, nullable=False)
    user = Column(Text, nullable=False)
    timestamp = Column(Float, nullable=False)
    annot_id = Column(Text, nullable=False)
    annot_type = Column(Text, nullable=False)
    annot_data = Column(Text, nullable=False)
    searchable_text = Column(Text, nullable=False, server_default=text("''"))
    id = Column(Integer, primary_key=True)


class AnnotationsDirtied(Base):
    __tablename__ = 'annotations_dirtied'

    book = Column(Integer, nullable=False, unique=True)
    id = Column(Integer, primary_key=True)


t_annotations_fts = Table(
    'annotations_fts', metadata,
    Column('searchable_text', Text)
)


class AnnotationsFtsConfig(Base):
    __tablename__ = 'annotations_fts_config'

    k = Column(Text, primary_key=True)
    v = Column(Text)


class AnnotationsFtsData(Base):
    __tablename__ = 'annotations_fts_data'

    id = Column(Integer, primary_key=True)
    block = Column(LargeBinary)


class AnnotationsFtsDocsize(Base):
    __tablename__ = 'annotations_fts_docsize'

    id = Column(Integer, primary_key=True)
    sz = Column(LargeBinary)


class AnnotationsFtsIdx(Base):
    __tablename__ = 'annotations_fts_idx'

    segid = Column(Text, primary_key=True, nullable=False)
    term = Column(Text, primary_key=True, nullable=False)
    pgno = Column(Text)


t_annotations_fts_stemmed = Table(
    'annotations_fts_stemmed', metadata,
    Column('searchable_text', Text)
)


class AnnotationsFtsStemmedConfig(Base):
    __tablename__ = 'annotations_fts_stemmed_config'

    k = Column(Text, primary_key=True)
    v = Column(Text)


class AnnotationsFtsStemmedData(Base):
    __tablename__ = 'annotations_fts_stemmed_data'

    id = Column(Integer, primary_key=True)
    block = Column(LargeBinary)


class AnnotationsFtsStemmedDocsize(Base):
    __tablename__ = 'annotations_fts_stemmed_docsize'

    id = Column(Integer, primary_key=True)
    sz = Column(LargeBinary)


class AnnotationsFtsStemmedIdx(Base):
    __tablename__ = 'annotations_fts_stemmed_idx'

    segid = Column(Text, primary_key=True, nullable=False)
    term = Column(Text, primary_key=True, nullable=False)
    pgno = Column(Text)


class BooksPluginData(Base):
    __tablename__ = 'books_plugin_data'
    __table_args__ = (
        UniqueConstraint('book', 'name'),
    )

    book = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    val = Column(Text, nullable=False)
    id = Column(Integer, primary_key=True)


class ConversionOptions(TimestampMixin, Base):
    __tablename__ = 'conversion_options'
    __table_args__ = (
        UniqueConstraint('format', 'book'),
        Index('conversion_options_idx_a', 'format'),
        Index('conversion_options_idx_b', 'book')
    )

    format = Column(Text, nullable=False)
    data = Column(LargeBinary, nullable=False)
    id = Column(Integer, primary_key=True)
    book = Column(Integer)

class Feeds(Base):
    __tablename__ = 'feeds'

    title = Column(Text, nullable=False, unique=True)
    script = Column(Text, nullable=False)
    id = Column(Integer, primary_key=True)


class LastReadPositions(Base):
    __tablename__ = 'last_read_positions'
    __table_args__ = (
        UniqueConstraint('user', 'device', 'book', 'format'),
        Index('lrp_idx', 'book')
    )

    book = Column(Integer, nullable=False)
    format = Column(Text, nullable=False)
    user = Column(Text, nullable=False)
    device = Column(Text, nullable=False)
    cfi = Column(Text, nullable=False)
    epoch = Column(Float, nullable=False)
    pos_frac = Column(Float, nullable=False, server_default=text('0'))
    id = Column(Integer, primary_key=True)

class Preferences(TimestampMixin, Base):
    __tablename__ = 'preferences'

    key = Column(Text, nullable=False, unique=True)
    val = Column(Text, nullable=False)
    id = Column(Integer, primary_key=True)

class BooksPagesLink(Books):
    __tablename__ = 'books_pages_link'

    __table_args__ = (
        Index('books_pages_link_pidx', 'needs_scan'),
    )

    pages = Column(Integer, nullable=False, server_default=text('0'))
    algorithm = Column(Integer, nullable=False, server_default=text('0'))
    format = Column(Text, nullable=False, server_default=text("''"))
    format_size = Column(Integer, nullable=False, server_default=text('0'))

    needs_scan = Column(
        Boolean,
        nullable=False,
        server_default=text('false')
    )

    book = Column(
        ForeignKey('books.id', ondelete='CASCADE'),
        primary_key=True
    )

    link_timestamp = Column(
        TIMESTAMP,
        server_default=text('CURRENT_TIMESTAMP')
    )