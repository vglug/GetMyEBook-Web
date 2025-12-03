# -*- coding: utf-8 -*-

"""
Discussion Forum Routes
Web routes for rendering discussion forum pages
"""

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from .. import db, logger, calibre_db
from .models import DiscussionThread
from ..db import Books , CalibreDB

# Create Blueprint
discussion_routes = Blueprint('discussion', __name__, url_prefix='/discussion')

log = logger.create()


@discussion_routes.route('/book/<int:book_id>')
@login_required
def book_discussion(book_id):
    try:
        book = calibre_db.get_book(book_id)
        if not book:
            flash("Book not found!", "error")
            log.error(f"Book with ID {book_id} not found.")
            return redirect(url_for('web.index'))

        flash(f'Discussion book id {book.id}', 'success')
        log.info(f"Loaded book '{book.title}' with ID: {book.id}")

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
        thread = calibre_db.session.query(DiscussionThread).get(thread_id)
        if not thread:
            abort(404)
        
        # Get book details
        book = calibre_db.session.query(Books).get(thread.book_id)
        if not book:
            abort(404)
        
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
        threads = calibre_db.session.query(DiscussionThread).filter_by(
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
        from .models import DiscussionThreadFollower
        
        # Get followed threads
        followed = calibre_db.session.query(DiscussionThreadFollower).filter_by(
            user_id=current_user.id
        ).all()
        
        thread_ids = [f.thread_id for f in followed]
        threads = calibre_db.session.query(DiscussionThread).filter(
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
