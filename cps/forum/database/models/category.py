from cps.forum import db
from cps.forum.database.models import Base


class Category(Base):
    __tablename__ = "forum_categories"
    
    name = db.Column(db.String(100))
    slug = db.Column(db.String(200))

    threads = db.relationship("Thread", back_populates="category")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug
        }


