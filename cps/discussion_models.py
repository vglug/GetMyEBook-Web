# -*- coding: utf-8 -*-

"""
Discussion Forum Database Models
Integrates with existing Calibre-Web database structure
"""

from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, 
    Integer, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from cps import db

# ============================================
# Discussion Thread Model
# ============================================
class DiscussionThread(db.Model):
    __tablename__ = 'discussion_threads'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    book_id = Column(BigInteger, ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, nullable=False)  # References user table
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    view_count = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    book = relationship('Books', foreign_keys=[book_id])
    comments = relationship('DiscussionComment', back_populates='thread', cascade='all, delete-orphan')
    followers = relationship('DiscussionThreadFollower', back_populates='thread', cascade='all, delete-orphan')
    
    def to_dict(self, include_comments=False):
        """Convert thread to dictionary"""
        data = {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'is_locked': self.is_locked,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'comment_count': len(self.comments) if self.comments else 0,
            'follower_count': len(self.followers) if self.followers else 0
        }
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.comments]
        
        return data
    
    def __repr__(self):
        return f'<DiscussionThread {self.id}: {self.title}>'


# ============================================
# Discussion Comment Model
# ============================================
class DiscussionComment(db.Model):
    __tablename__ = 'discussion_comments'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(BigInteger, ForeignKey('discussion_threads.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    parent_comment_id = Column(BigInteger, ForeignKey('discussion_comments.id', ondelete='CASCADE'), nullable=True)
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    thread = relationship('DiscussionThread', back_populates='comments')
    parent = relationship('DiscussionComment', remote_side=[id], backref='replies')
    likes = relationship('DiscussionCommentLike', back_populates='comment', cascade='all, delete-orphan')
    
    def to_dict(self, include_replies=False):
        """Convert comment to dictionary"""
        data = {
            'id': self.id,
            'thread_id': self.thread_id,
            'user_id': self.user_id,
            'parent_comment_id': self.parent_comment_id,
            'content': self.content,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'like_count': len(self.likes) if self.likes else 0
        }
        
        if include_replies and hasattr(self, 'replies'):
            data['replies'] = [reply.to_dict() for reply in self.replies]
        
        return data
    
    def __repr__(self):
        return f'<DiscussionComment {self.id} on Thread {self.thread_id}>'


# ============================================
# Comment Likes Model
# ============================================
class DiscussionCommentLike(db.Model):
    __tablename__ = 'discussion_comment_likes'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    comment_id = Column(BigInteger, ForeignKey('discussion_comments.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    reaction_type = Column(String(20), default='like')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    comment = relationship('DiscussionComment', back_populates='likes')
    
    def to_dict(self):
        """Convert like to dictionary"""
        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'user_id': self.user_id,
            'reaction_type': self.reaction_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CommentLike {self.id} by User {self.user_id}>'


# ============================================
# Thread Followers Model
# ============================================
class DiscussionThreadFollower(db.Model):
    __tablename__ = 'discussion_thread_followers'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    thread_id = Column(BigInteger, ForeignKey('discussion_threads.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    notify_on_reply = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    thread = relationship('DiscussionThread', back_populates='followers')
    
    def to_dict(self):
        """Convert follower to dictionary"""
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'user_id': self.user_id,
            'notify_on_reply': self.notify_on_reply,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ThreadFollower {self.id}: User {self.user_id} follows Thread {self.thread_id}>'


# ============================================
# Reported Content Model
# ============================================
class DiscussionReport(db.Model):
    __tablename__ = 'discussion_reports'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reporter_user_id = Column(BigInteger, nullable=False)
    content_type = Column(String(20), nullable=False)  # 'thread' or 'comment'
    content_id = Column(BigInteger, nullable=False)
    reason = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default='pending')
    reviewed_by_user_id = Column(BigInteger, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'id': self.id,
            'reporter_user_id': self.reporter_user_id,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'reviewed_by_user_id': self.reviewed_by_user_id,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<DiscussionReport {self.id}: {self.content_type} {self.content_id}>'


# ============================================
# User Reputation Model
# ============================================
class DiscussionUserReputation(db.Model):
    __tablename__ = 'discussion_user_reputation'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    total_points = Column(BigInteger, default=0)
    threads_created = Column(BigInteger, default=0)
    comments_posted = Column(BigInteger, default=0)
    helpful_votes_received = Column(BigInteger, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert reputation to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_points': self.total_points,
            'threads_created': self.threads_created,
            'comments_posted': self.comments_posted,
            'helpful_votes_received': self.helpful_votes_received,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserReputation User {self.user_id}: {self.total_points} points>'
