"""
Forum Database Models
=====================
All SQLAlchemy models for the GetMyEBook forum feature live here.

Path: cps/models/forum/
"""
from cps.forum import db


class Base(db.Model):
    __abstract__ = True

    json_attributes = ()

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def update(self, attributes):
        """Bulk-update columns and persist immediately."""
        for key, value in attributes.items():
            setattr(self, key, value)
        self.save()

    def save(self):
        """Add this instance to the session and commit."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete this instance from the session and commit."""
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        """Serialize declared json_attributes to a dict."""
        attributes = {}
        for key in self.json_attributes:
            attributes[key] = getattr(self, key)
        return attributes

    def increment(self, column):
        """Increment a numeric column by 1 and persist."""
        column_value = getattr(self, column, 0)
        self.update({column: column_value + 1})

    def decrement(self, column):
        """Decrement a numeric column by 1 (min 0) and persist."""
        column_value = getattr(self, column, 0)
        if column_value > 0:
            self.update({column: column_value - 1})


# User is resolved dynamically through properties on Thread / Comment to
# avoid cross-database SQLAlchemy relationship conflicts.
from .category import Category          # noqa: E402
from .thread import Thread              # noqa: E402
from .comment import Comment            # noqa: E402
from .like import CommentLike           # noqa: E402
from .emoji import Emoji                # noqa: E402

__all__ = [
    "Base",
    "Category",
    "Thread",
    "Comment",
    "CommentLike",
    "Emoji",
]
