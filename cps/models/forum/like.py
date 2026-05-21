"""
CommentLike Model
=================
Stores per-user reactions (like, love, haha, …) on individual comments.
Each (user_id, comment_id) pair is unique — a user can only react once per comment.
"""
from cps.forum import db
from cps.models.forum import Base


class CommentLike(Base):
    """A single user reaction attached to one comment."""

    __tablename__ = "forum_comment_likes"

    user_id = db.Column(db.Integer, nullable=False)
    comment_id = db.Column(
        db.Integer,
        db.ForeignKey("forum_comments.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Reaction type: 'like' | 'love' | 'haha' | 'wow' | 'sad' | 'angry'
    reaction_type = db.Column(db.String(20), default="like", nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "comment_id", name="unique_user_comment_like"
        ),
    )

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "comment_id": self.comment_id,
            "reaction_type": self.reaction_type,
        }

    def __repr__(self):
        return (
            f"<CommentLike id={self.id} user={self.user_id} "
            f"comment={self.comment_id} reaction={self.reaction_type!r}>"
        )
