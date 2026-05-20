"""
Comment Model
=============
Represents a user comment on a forum thread.
Supports nested replies via a self-referential parent/replies relationship.
User ownership is resolved dynamically from the main app's `ub.User` to
avoid cross-database SQLAlchemy conflicts.
"""
from cps.forum import db
from cps.models.forum import Base


class Comment(Base):
    """A single comment (or reply) posted inside a forum thread."""

    __tablename__ = "forum_comments"

    content = db.Column(db.Text, nullable=False)

    # References main app's users table — FK constraint intentionally omitted
    # to avoid metadata mismatch across separate DB instances.
    user_id = db.Column(db.Integer, nullable=False)

    thread_id = db.Column(
        db.Integer,
        db.ForeignKey("forum_threads.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Self-referential: a comment can be a reply to another comment
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("forum_comments.id", ondelete="CASCADE"),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    thread = db.relationship("Thread", back_populates="comments")

    likes = db.relationship(
        "CommentLike",
        backref="comment",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side="Comment.id"),
        cascade="all, delete-orphan",
        lazy="select",           # Marshmallow / JSON triggers load
        order_by="Comment.created_at",
    )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def likes_count(self):
        """Total number of reactions on this comment."""
        return self.likes.count()

    @property
    def liked_by_current_user(self):
        """True if the currently authenticated user has reacted to this comment."""
        from flask_login import current_user
        if not current_user.is_authenticated:
            return False
        return self.likes.filter_by(user_id=current_user.id).first() is not None

    @property
    def current_user_reaction(self):
        """Return the reaction_type the current user posted, or None."""
        from flask_login import current_user
        if not current_user.is_authenticated:
            return None
        like = self.likes.filter_by(user_id=current_user.id).first()
        return like.reaction_type if like else None

    @property
    def top_reaction(self):
        """Return the most common reaction_type for this comment, or None."""
        from sqlalchemy import func
        from cps.models.forum.like import CommentLike

        if self.likes_count == 0:
            return None
        try:
            top = (
                self.likes
                .with_entities(
                    CommentLike.reaction_type,
                    func.count(CommentLike.reaction_type).label("cnt"),
                )
                .group_by(CommentLike.reaction_type)
                .order_by(func.count(CommentLike.reaction_type).desc())
                .first()
            )
            return top.reaction_type if top else None
        except Exception:
            return "like"   # safe fallback

    @property
    def owner(self):
        """Resolve the comment author from the main app's users table."""
        if not self.user_id:
            return None
        from cps import ub
        return ub.session.query(ub.User).filter(ub.User.id == self.user_id).first()

    @property
    def is_reply(self):
        """True when this comment is a reply to another comment."""
        return self.parent_id is not None

    @property
    def replies_count(self):
        """Number of direct replies to this comment."""
        return len(self.replies) if self.replies else 0

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def is_owner(self, user):
        """Return True if *user* is the author of this comment."""
        return user is not None and user.id == self.user_id

    def get_all_replies(self):
        """Recursively collect all nested replies into a flat list."""
        all_replies = []
        for reply in self.replies:
            all_replies.append(reply)
            all_replies.extend(reply.get_all_replies())
        return all_replies

    def to_json(self):
        owner = self.owner
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id,
            "thread_id": self.thread_id,
            "parent_id": self.parent_id,
            "created_at": str(self.created_at) if self.created_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None,
            "likes_count": self.likes_count,
            "replies_count": self.replies_count,
            "is_reply": self.is_reply,
            "top_reaction": self.top_reaction,
            "current_user_reaction": self.current_user_reaction,
            "owner": {
                "id": owner.id,
                "name": owner.name,
            } if owner else None,
        }

    def __repr__(self):
        return f"<Comment id={self.id} thread={self.thread_id} user={self.user_id}>"
