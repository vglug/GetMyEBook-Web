from cps.forum.database.models import Base
from cps.forum import db


class Comment(Base):
    __tablename__ = "forum_comments"

    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("forum_users.id"))
    thread_id = db.Column(db.Integer, db.ForeignKey("forum_threads.id"))
    
    owner = db.relationship("User", back_populates="comments")
    thread = db.relationship("Thread", back_populates="comments")

    def is_owner(self, user):
        print(self.user_id, user.id)
        return self.owner == user
