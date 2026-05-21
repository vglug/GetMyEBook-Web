"""
Category Model
==============
Represents a forum category that groups related threads together.
"""
from cps.forum import db
from cps.models.forum import Base


class Category(Base):
    """A top-level grouping for forum threads (e.g. 'General', 'Book Discussion')."""

    __tablename__ = "forum_categories"

    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # One-to-many: a category has many threads
    threads = db.relationship("Thread", back_populates="category", lazy="dynamic")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "created_at": str(self.created_at) if self.created_at else None,
            "threads_count": self.threads.count() if self.threads else 0,
        }

    def __repr__(self):
        return f"<Category id={self.id} name={self.name!r}>"
