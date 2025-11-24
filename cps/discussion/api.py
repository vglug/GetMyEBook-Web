# -*- coding: utf-8 -*-

"""
Discussion Forum REST API
Provides endpoints for managing book discussions
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from .. import db, logger
from .models import (
    DiscussionThread, DiscussionComment, DiscussionCommentLike,
    DiscussionThreadFollower, DiscussionReport, DiscussionUserReputation
)

# Create Blueprint
discussion_api = Blueprint('discussion_api', __name__, url_prefix='/api/discussion')

log = logger.create()


# ============================================
# Helper Functions
# ============================================

def get_current_user_id():
    """Get current user ID from session"""
    if current_user.is_authenticated:
        return current_user.id
    return None


def validate_user_permission(user_id):
    """Check if user has permission to perform action"""
    current_id = get_current_user_id()
    if not current_id:
        return False, "User not authenticated"
    if current_id != user_id and not current_user.role_admin():
        return False, "Insufficient permissions"
    return True, None


# ============================================
# Thread Endpoints
# ============================================

@discussion_api.route('/books/<int:book_id>/threads', methods=['GET'])
def get_book_threads(book_id):
    """Get all discussion threads for a specific book"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort', 'recent')  # recent, popular, oldest
        
        # Base query
        query = DiscussionThread.query.filter_by(book_id=book_id)
        
        # Apply sorting
        if sort_by == 'popular':
            query = query.order_by(desc(DiscussionThread.view_count))
        elif sort_by == 'oldest':
            query = query.order_by(DiscussionThread.created_at)
        else:  # recent
            query = query.order_by(desc(DiscussionThread.last_activity_at))
        
        # Pinned threads always on top
        query = query.order_by(desc(DiscussionThread.is_pinned))
        
        # Paginate
        threads = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'threads': [thread.to_dict() for thread in threads.items],
            'total': threads.total,
            'pages': threads.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        log.error(f"Error fetching threads for book {book_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@discussion_api.route('/threads/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get a specific discussion thread with all comments"""
    try:
        thread = DiscussionThread.query.get_or_404(thread_id)
        
        # Increment view count
        thread.view_count += 1
        db.session.commit()
        
        # Get comments with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        comments_query = DiscussionComment.query.filter_by(
            thread_id=thread_id,
            parent_comment_id=None  # Only top-level comments
        ).order_by(DiscussionComment.created_at)
        
        comments = comments_query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'thread': thread.to_dict(),
            'comments': [comment.to_dict(include_replies=True) for comment in comments.items],
            'total_comments': comments.total,
            'pages': comments.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        log.error(f"Error fetching thread {thread_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@discussion_api.route('/books/<int:book_id>/threads', methods=['POST'])
@login_required
def create_thread(book_id):
    """Create a new discussion thread"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Title and content are required'}), 400
        
        thread = DiscussionThread(
            book_id=book_id,
            user_id=current_user.id,
            title=data['title'],
            content=data['content']
        )
        
        db.session.add(thread)
        db.session.commit()
        
        # Auto-follow the thread
        follower = DiscussionThreadFollower(
            thread_id=thread.id,
            user_id=current_user.id
        )
        db.session.add(follower)
        db.session.commit()
        
        log.info(f"User {current_user.id} created thread {thread.id} for book {book_id}")
        
        return jsonify({
            'success': True,
            'thread': thread.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error creating thread: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@discussion_api.route('/threads/<int:thread_id>', methods=['PUT'])
@login_required
def update_thread(thread_id):
    """Update a discussion thread"""
    try:
        thread = DiscussionThread.query.get_or_404(thread_id)
        
        # Check permissions
        is_valid, error = validate_user_permission(thread.user_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            thread.title = data['title']
        if 'content' in data:
            thread.content = data['content']
        if 'is_pinned' in data and current_user.role_admin():
            thread.is_pinned = data['is_pinned']
        if 'is_locked' in data and current_user.role_admin():
            thread.is_locked = data['is_locked']
        
        thread.updated_at = datetime.utcnow()
        db.session.commit()
        
        log.info(f"Thread {thread_id} updated by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'thread': thread.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error updating thread {thread_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@discussion_api.route('/threads/<int:thread_id>', methods=['DELETE'])
@login_required
def delete_thread(thread_id):
    """Delete a discussion thread"""
    try:
        thread = DiscussionThread.query.get_or_404(thread_id)
        
        # Check permissions
        is_valid, error = validate_user_permission(thread.user_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 403
        
        db.session.delete(thread)
        db.session.commit()
        
        log.info(f"Thread {thread_id} deleted by user {current_user.id}")
        
        return jsonify({'success': True, 'message': 'Thread deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error deleting thread {thread_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Comment Endpoints
# ============================================

@discussion_api.route('/threads/<int:thread_id>/comments', methods=['POST'])
@login_required
def create_comment(thread_id):
    """Create a new comment on a thread"""
    try:
        thread = DiscussionThread.query.get_or_404(thread_id)
        
        if thread.is_locked and not current_user.role_admin():
            return jsonify({'success': False, 'error': 'Thread is locked'}), 403
        
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        comment = DiscussionComment(
            thread_id=thread_id,
            user_id=current_user.id,
            content=data['content'],
            parent_comment_id=data.get('parent_comment_id')
        )
        
        db.session.add(comment)
        
        # Update thread activity
        thread.last_activity_at = datetime.utcnow()
        
        db.session.commit()
        
        log.info(f"User {current_user.id} commented on thread {thread_id}")
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error creating comment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@discussion_api.route('/comments/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(comment_id):
    """Update a comment"""
    try:
        comment = DiscussionComment.query.get_or_404(comment_id)
        
        # Check permissions
        is_valid, error = validate_user_permission(comment.user_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 403
        
        data = request.get_json()
        
        if 'content' in data:
            comment.content = data['content']
            comment.is_edited = True
            comment.edited_at = datetime.utcnow()
        
        db.session.commit()
        
        log.info(f"Comment {comment_id} updated by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error updating comment {comment_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@discussion_api.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        comment = DiscussionComment.query.get_or_404(comment_id)
        
        # Check permissions
        is_valid, error = validate_user_permission(comment.user_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        log.info(f"Comment {comment_id} deleted by user {current_user.id}")
        
        return jsonify({'success': True, 'message': 'Comment deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error deleting comment {comment_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Like/Reaction Endpoints
# ============================================

@discussion_api.route('/comments/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Like/unlike a comment"""
    try:
        comment = DiscussionComment.query.get_or_404(comment_id)
        
        # Check if already liked
        existing_like = DiscussionCommentLike.query.filter_by(
            comment_id=comment_id,
            user_id=current_user.id
        ).first()
        
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'unliked',
                'like_count': len(comment.likes)
            }), 200
        else:
            # Like
            like = DiscussionCommentLike(
                comment_id=comment_id,
                user_id=current_user.id,
                reaction_type='like'
            )
            db.session.add(like)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'action': 'liked',
                'like_count': len(comment.likes)
            }), 201
            
    except Exception as e:
        db.session.rollback()
        log.error(f"Error liking comment {comment_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Thread Following Endpoints
# ============================================

@discussion_api.route('/threads/<int:thread_id>/follow', methods=['POST'])
@login_required
def follow_thread(thread_id):
    """Follow/unfollow a thread"""
    try:
        thread = DiscussionThread.query.get_or_404(thread_id)
        
        # Check if already following
        existing_follow = DiscussionThreadFollower.query.filter_by(
            thread_id=thread_id,
            user_id=current_user.id
        ).first()
        
        if existing_follow:
            # Unfollow
            db.session.delete(existing_follow)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'unfollowed'
            }), 200
        else:
            # Follow
            follower = DiscussionThreadFollower(
                thread_id=thread_id,
                user_id=current_user.id
            )
            db.session.add(follower)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'action': 'followed'
            }), 201
            
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Already following this thread'}), 400
    except Exception as e:
        db.session.rollback()
        log.error(f"Error following thread {thread_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Report Endpoints
# ============================================

@discussion_api.route('/report', methods=['POST'])
@login_required
def report_content():
    """Report inappropriate content"""
    try:
        data = request.get_json()
        
        required_fields = ['content_type', 'content_id', 'reason']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        report = DiscussionReport(
            reporter_user_id=current_user.id,
            content_type=data['content_type'],
            content_id=data['content_id'],
            reason=data['reason'],
            description=data.get('description', '')
        )
        
        db.session.add(report)
        db.session.commit()
        
        log.info(f"Content reported by user {current_user.id}: {data['content_type']} {data['content_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Content reported successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log.error(f"Error reporting content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# User Statistics Endpoints
# ============================================

@discussion_api.route('/users/<int:user_id>/reputation', methods=['GET'])
def get_user_reputation(user_id):
    """Get user reputation and statistics"""
    try:
        reputation = DiscussionUserReputation.query.filter_by(user_id=user_id).first()
        
        if not reputation:
            # Create default reputation entry
            reputation = DiscussionUserReputation(user_id=user_id)
            db.session.add(reputation)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'reputation': reputation.to_dict()
        }), 200
        
    except Exception as e:
        log.error(f"Error fetching reputation for user {user_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Search Endpoint
# ============================================

@discussion_api.route('/search', methods=['GET'])
def search_discussions():
    """Search discussions by keyword"""
    try:
        query_text = request.args.get('q', '')
        book_id = request.args.get('book_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not query_text:
            return jsonify({'success': False, 'error': 'Search query is required'}), 400
        
        # Search in threads
        query = DiscussionThread.query.filter(
            or_(
                DiscussionThread.title.ilike(f'%{query_text}%'),
                DiscussionThread.content.ilike(f'%{query_text}%')
            )
        )
        
        if book_id:
            query = query.filter_by(book_id=book_id)
        
        threads = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'results': [thread.to_dict() for thread in threads.items],
            'total': threads.total,
            'pages': threads.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        log.error(f"Error searching discussions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
