# -*- coding: utf-8 -*-

"""
Discussion Forum Module
Provides discussion functionality for books in Calibre-Web
"""

from .models import (
    DiscussionThread,
    DiscussionComment,
    DiscussionCommentLike,
    DiscussionThreadFollower,
    DiscussionReport,
    DiscussionUserReputation
)

from .api import discussion_api
from .routes import discussion_routes

__all__ = [
    'DiscussionThread',
    'DiscussionComment',
    'DiscussionCommentLike',
    'DiscussionThreadFollower',
    'DiscussionReport',
    'DiscussionUserReputation',
    'discussion_api',
    'discussion_routes'
]
