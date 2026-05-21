"""
Thread Model
============
Represents a forum thread linked to a specific book in the Calibre library.
User ownership is resolved dynamically from the main app's `ub.User` to
avoid cross-database SQLAlchemy conflicts.
"""
from sqlalchemy.ext.hybrid import hybrid_property

from cps.forum import db
from cps.models.forum import Base
from cps.models.forum.comment import Comment


class Thread(Base):
    """A forum discussion thread tied to one book."""

    __tablename__ = "forum_threads"

    json_attributes = (
        "id", "title", "slug", "content",
        "user_id", "category_id", "comments_count", "book_id",
    )

    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), nullable=False, unique=True)
    content = db.Column(db.Text)

    # References main app's users table — FK omitted intentionally
    user_id = db.Column(db.Integer, nullable=False)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("forum_categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Each book can have at most one discussion thread
    book_id = db.Column(db.Integer, nullable=False, unique=True)

    views_count = db.Column(db.Integer, nullable=False, default=0)
    comments_count = db.Column(db.Integer, nullable=False, default=0)
    best_comment_id = db.Column(db.Integer, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    category = db.relationship("Category", back_populates="threads")

    comments = db.relationship(
        "Comment",
        back_populates="thread",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="Comment.created_at",
    )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def owner(self):
        """Resolve the thread author from the main app's users table."""
        if not self.user_id:
            return None
        from cps import ub
        return ub.session.query(ub.User).filter(ub.User.id == self.user_id).first()

    @property
    def summary(self):
        """Return the first 300 characters of the thread content."""
        if not self.content:
            return ""
        return self.content[:300] + ("..." if len(self.content) > 300 else "")

    @hybrid_property
    def has_comments(self):
        """True when at least one comment exists on this thread."""
        return self.comments_count > 0

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def is_owner(self, user):
        """Return True if *user* is the author of this thread."""
        return user is not None and user.id == self.user_id

    def add_comment(self, content, owner):
        """Create and persist a new top-level comment on this thread."""
        comment = Comment(content=content, user_id=owner.id, thread_id=self.id)
        comment.save()
        self.increment("comments_count")
        return comment

    def increment_views(self):
        """Record one page-view for this thread."""
        self.increment("views_count")

    @staticmethod
    def thread_rollback():
        """Roll back the current forum DB session (used in error handlers)."""
        db.session.rollback()

    def to_json(self):
        owner = self.owner
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "content": self.content,
            "summary": self.summary,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "book_id": self.book_id,
            "views_count": self.views_count,
            "comments_count": self.comments_count,
            "best_comment_id": self.best_comment_id,
            "has_comments": self.has_comments,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
            "owner": {
                "id": owner.id,
                "name": owner.name,
            } if owner else None,
            "category": self.category.to_json() if self.category else None,
        }

    def __repr__(self):
        return f"<Thread id={self.id} slug={self.slug!r} book={self.book_id}>"
