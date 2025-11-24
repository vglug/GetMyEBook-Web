# Discussion Module

This module provides complete discussion forum functionality for Calibre-Web books.

## Structure

- `__init__.py` - Module initialization and public API
- `models.py` - SQLAlchemy database models (6 models)
- `api.py` - REST API endpoints (Blueprint: `/api/discussion`)
- `routes.py` - Web UI routes (Blueprint: `/discussion`)

## Database Models

1. **DiscussionThread** - Main discussion topics for books
2. **DiscussionComment** - Comments and nested replies
3. **DiscussionCommentLike** - User reactions to comments
4. **DiscussionThreadFollower** - Thread subscriptions
5. **DiscussionReport** - Content moderation reports
6. **DiscussionUserReputation** - User activity statistics

## Usage

The module is automatically imported in `cps/main.py`:

```python
from .discussion import discussion_api, discussion_routes

app.register_blueprint(discussion_api)      # /api/discussion/*
app.register_blueprint(discussion_routes)   # /discussion/*
```

## API Endpoints

### Threads
- `GET /api/discussion/books/{book_id}/threads` - List threads
- `POST /api/discussion/books/{book_id}/threads` - Create thread
- `GET /api/discussion/threads/{thread_id}` - Get thread details
- `PUT /api/discussion/threads/{thread_id}` - Update thread
- `DELETE /api/discussion/threads/{thread_id}` - Delete thread

### Comments
- `POST /api/discussion/threads/{thread_id}/comments` - Add comment
- `PUT /api/discussion/comments/{comment_id}` - Update comment
- `DELETE /api/discussion/comments/{comment_id}` - Delete comment
- `POST /api/discussion/comments/{comment_id}/like` - Like/unlike

### Other
- `POST /api/discussion/threads/{thread_id}/follow` - Follow/unfollow
- `POST /api/discussion/report` - Report content
- `GET /api/discussion/users/{user_id}/reputation` - User stats
- `GET /api/discussion/search?q={query}` - Search discussions

## Web Routes

- `/discussion/book/{book_id}` - Discussion forum for a book
- `/discussion/thread/{thread_id}` - View specific thread
- `/discussion/my-discussions` - User's created discussions
- `/discussion/following` - Followed discussions

## Templates

Located in `cps/templates/`:
- `discussion_forum.html` - Main forum listing
- `discussion_thread.html` - Thread detail view

## Documentation

Comprehensive documentation is available in `/docs/discussion/`:
- [README.md](../../docs/discussion/README.md) - Overview and summary
- [guide.md](../../docs/discussion/guide.md) - Complete implementation guide
- [quick-start.md](../../docs/discussion/quick-start.md) - Quick reference
- [integration.md](../../docs/discussion/integration.md) - Integration examples
- [schema.sql](../../docs/discussion/schema.sql) - PostgreSQL database schema

## Database Setup

Run the setup script:
```bash
./scripts/setup_discussion_forum.sh
```

Or manually:
```bash
psql -U username -d database_name -f docs/discussion/schema.sql
```

## Testing

```python
# Test imports
from cps.discussion import discussion_api, discussion_routes
from cps.discussion.models import DiscussionThread

# Test blueprint registration
print(discussion_api.name)  # 'discussion_api'
print(discussion_routes.name)  # 'discussion'
```

## Dependencies

- Flask
- Flask-Login
- SQLAlchemy
- PostgreSQL database (configured in `.env`)

## Integration Points

### Book Detail Page
Add discussion link:
```html
<a href="{{ url_for('discussion.book_discussion', book_id=book.id) }}" 
   class="btn btn-primary">
    <i class="bi bi-chat-dots"></i> Discussion
</a>
```

### Navigation Menu
Add discussion menu item to `layout.html`

## Maintainers

For questions or issues, see the main documentation in `/docs/discussion/`.
