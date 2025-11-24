# -*- coding: utf-8 -*-

"""
Discussion Forum Routes
Web routes for rendering discussion forum pages
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from cps import db, logger
from cps.discussion_models import DiscussionThread
from cps.db import Books

# Create Blueprint
discussion_routes = Blueprint('discussion', __name__, url_prefix='/discussion')

log = logger.create()


@discussion_routes.route('/book/<int:book_id>')
@login_required
def book_discussion(book_id):
    """
    Display discussion forum for a specific book
    """
    try:
        # Get book details
        book = Books.query.get_or_404(book_id)
        
        # Render discussion forum page
        return render_template(
            'discussion_forum.html',
            book=book,
            title=f'Discussion - {book.title}'
        )
        
    except SQLAlchemyError as e:
        log.error(f"Database error loading discussion for book {book_id}: {str(e)}")
        flash('Error loading discussion forum', 'error')
        return redirect(url_for('web.show_book', book_id=book_id))
    except Exception as e:
        log.error(f"Error loading discussion for book {book_id}: {str(e)}")
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('web.index'))


@discussion_routes.route('/thread/<int:thread_id>')
@login_required
def view_thread(thread_id):
    """
    Display a specific discussion thread with all comments
    """
    try:
        # Get thread details
        thread = DiscussionThread.query.get_or_404(thread_id)
        
        # Get book details
        book = Books.query.get_or_404(thread.book_id)
        
        # Render thread detail page
        return render_template(
            'discussion_thread.html',
            thread=thread,
            book=book,
            title=thread.title
        )
        
    except SQLAlchemyError as e:
        log.error(f"Database error loading thread {thread_id}: {str(e)}")
        flash('Error loading discussion thread', 'error')
        return redirect(url_for('discussion.book_discussion', book_id=thread.book_id))
    except Exception as e:
        log.error(f"Error loading thread {thread_id}: {str(e)}")
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('web.index'))


@discussion_routes.route('/my-discussions')
@login_required
def my_discussions():
    """
    Display all discussions created by the current user
    """
    try:
        # Get user's threads
        threads = DiscussionThread.query.filter_by(
            user_id=current_user.id
        ).order_by(DiscussionThread.created_at.desc()).all()
        
        return render_template(
            'my_discussions.html',
            threads=threads,
            title='My Discussions'
        )
        
    except Exception as e:
        log.error(f"Error loading user discussions: {str(e)}")
        flash('Error loading your discussions', 'error')
        return redirect(url_for('web.index'))


@discussion_routes.route('/following')
@login_required
def following_discussions():
    """
    Display all discussions the user is following
    """
    try:
        from cps.discussion_models import DiscussionThreadFollower
        
        # Get followed threads
        followed = DiscussionThreadFollower.query.filter_by(
            user_id=current_user.id
        ).all()
        
        thread_ids = [f.thread_id for f in followed]
        threads = DiscussionThread.query.filter(
            DiscussionThread.id.in_(thread_ids)
        ).order_by(DiscussionThread.last_activity_at.desc()).all()
        
        return render_template(
            'following_discussions.html',
            threads=threads,
            title='Following Discussions'
        )
        
    except Exception as e:
        log.error(f"Error loading followed discussions: {str(e)}")
        flash('Error loading followed discussions', 'error')
        return redirect(url_for('web.index'))
