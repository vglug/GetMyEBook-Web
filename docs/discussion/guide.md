# Discussion Forum Integration Guide

## Overview

This is a complete discussion forum system for your GetMyEBook-Web application. It allows users to create discussions about books, post comments, like comments, follow threads, and more.

## Features

### Core Features
- ✅ **Thread Management**: Create, read, update, delete discussion threads
- ✅ **Comments & Replies**: Nested comment system with unlimited depth
- ✅ **Likes/Reactions**: Users can like comments
- ✅ **Thread Following**: Subscribe to threads for notifications
- ✅ **Moderation**: Report inappropriate content, lock/pin threads
- ✅ **User Reputation**: Track user activity and points
- ✅ **Search**: Search discussions by keywords
- ✅ **Sorting**: Sort by recent, popular, or oldest
- ✅ **Pagination**: Efficient loading of large discussions

### UI Features
- 🎨 Modern, responsive Bootstrap 5 design
- 🌈 Beautiful gradient backgrounds and animations
- 📱 Mobile-friendly interface
- ⚡ Real-time updates via AJAX
- 🎭 Smooth transitions and micro-animations

## Installation Steps

### 1. Database Setup

Run the SQL schema to create the necessary tables:

```bash
psql -U vglug -d your_database_name -f discussion_forum_schema.sql
```

Or manually execute the SQL in your PostgreSQL client.

### 2. Register Blueprints

Edit your main application file (`cps/__init__.py` or `cps.py`) and add:

```python
from cps.discussion_api import discussion_api
from cps.discussion_routes import discussion_routes

# Register blueprints
app.register_blueprint(discussion_api)
app.register_blueprint(discussion_routes)
```

### 3. Update Book Detail Page

Add a "Discussion" tab to your book detail page. In your book detail template (e.g., `templates/detail.html`), add:

```html
<!-- Add this to your tabs navigation -->
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('discussion.book_discussion', book_id=book.id) }}">
        <i class="bi bi-chat-dots"></i> Discussion
    </a>
</li>
```

Or add a button:

```html
<a href="{{ url_for('discussion.book_discussion', book_id=book.id) }}" 
   class="btn btn-primary">
    <i class="bi bi-chat-dots"></i> Join Discussion
</a>
```

### 4. Update Navigation Menu

Add discussion links to your main navigation (in `templates/base.html` or similar):

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('discussion.my_discussions') }}">
        My Discussions
    </a>
</li>
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('discussion.following_discussions') }}">
        Following
    </a>
</li>
```

## API Endpoints

### Thread Endpoints

#### Get All Threads for a Book
```
GET /api/discussion/books/{book_id}/threads
Query Parameters:
  - page: int (default: 1)
  - per_page: int (default: 20)
  - sort: string (recent|popular|oldest)
```

#### Get Single Thread
```
GET /api/discussion/threads/{thread_id}
Query Parameters:
  - page: int (default: 1)
  - per_page: int (default: 50)
```

#### Create Thread
```
POST /api/discussion/books/{book_id}/threads
Body: {
  "title": "Thread title",
  "content": "Thread content"
}
```

#### Update Thread
```
PUT /api/discussion/threads/{thread_id}
Body: {
  "title": "Updated title",
  "content": "Updated content",
  "is_pinned": true,  // Admin only
  "is_locked": false  // Admin only
}
```

#### Delete Thread
```
DELETE /api/discussion/threads/{thread_id}
```

### Comment Endpoints

#### Create Comment
```
POST /api/discussion/threads/{thread_id}/comments
Body: {
  "content": "Comment content",
  "parent_comment_id": 123  // Optional, for replies
}
```

#### Update Comment
```
PUT /api/discussion/comments/{comment_id}
Body: {
  "content": "Updated content"
}
```

#### Delete Comment
```
DELETE /api/discussion/comments/{comment_id}
```

#### Like/Unlike Comment
```
POST /api/discussion/comments/{comment_id}/like
```

### Other Endpoints

#### Follow/Unfollow Thread
```
POST /api/discussion/threads/{thread_id}/follow
```

#### Report Content
```
POST /api/discussion/report
Body: {
  "content_type": "thread|comment",
  "content_id": 123,
  "reason": "spam|offensive|inappropriate",
  "description": "Optional description"
}
```

#### Get User Reputation
```
GET /api/discussion/users/{user_id}/reputation
```

#### Search Discussions
```
GET /api/discussion/search
Query Parameters:
  - q: string (search query)
  - book_id: int (optional)
  - page: int (default: 1)
  - per_page: int (default: 20)
```

## Database Schema

### Tables

1. **discussion_threads**
   - Main discussion threads for each book
   - Fields: id, book_id, user_id, title, content, is_pinned, is_locked, view_count, timestamps

2. **discussion_comments**
   - Comments and replies on threads
   - Fields: id, thread_id, user_id, parent_comment_id, content, is_edited, timestamps

3. **discussion_comment_likes**
   - User likes/reactions on comments
   - Fields: id, comment_id, user_id, reaction_type, created_at

4. **discussion_thread_followers**
   - Users following specific threads
   - Fields: id, thread_id, user_id, notify_on_reply, created_at

5. **discussion_reports**
   - Reported content for moderation
   - Fields: id, reporter_user_id, content_type, content_id, reason, status, timestamps

6. **discussion_user_reputation**
   - User activity statistics and points
   - Fields: id, user_id, total_points, threads_created, comments_posted, helpful_votes_received

### Automatic Features

- **Triggers**: Automatically update thread activity when comments are added
- **Reputation System**: Auto-increment user points for participation
- **Views**: Pre-built views for common statistics queries

## Customization

### Styling

All styles are in the `<style>` section of the templates. You can customize:

- **Colors**: Modify CSS variables in `:root`
- **Fonts**: Change the Google Fonts import
- **Animations**: Adjust `@keyframes` definitions
- **Layout**: Modify Bootstrap classes

### Permissions

The system uses Flask-Login for authentication. Customize permissions in `discussion_api.py`:

```python
def validate_user_permission(user_id):
    # Add your custom permission logic here
    pass
```

### Reputation Points

Modify point values in the database triggers:

```sql
-- In discussion_forum_schema.sql
-- Change these values:
total_points = discussion_user_reputation.total_points + 5  -- Thread creation
total_points = discussion_user_reputation.total_points + 2  -- Comment posting
```

## Testing

### Manual Testing

1. **Create a Thread**
   - Navigate to a book page
   - Click "Discussion" tab
   - Click "Start New Discussion"
   - Fill in title and content
   - Submit

2. **Add Comments**
   - Open a thread
   - Type in the comment box
   - Click "Post Comment"

3. **Test Replies**
   - Click "Reply" on any comment
   - Type your reply
   - Submit

4. **Test Likes**
   - Click the heart icon on any comment
   - Verify the count increases

### API Testing with cURL

```bash
# Get threads for book ID 1
curl http://localhost:8083/api/discussion/books/1/threads

# Create a thread (requires authentication)
curl -X POST http://localhost:8083/api/discussion/books/1/threads \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Thread","content":"Test content"}'

# Like a comment
curl -X POST http://localhost:8083/api/discussion/comments/1/like
```

## Troubleshooting

### Common Issues

1. **"Table does not exist" error**
   - Solution: Run the SQL schema file to create tables

2. **"Blueprint not registered" error**
   - Solution: Make sure you registered both blueprints in your app

3. **"User not authenticated" error**
   - Solution: Ensure Flask-Login is properly configured

4. **Comments not loading**
   - Solution: Check browser console for JavaScript errors
   - Verify API endpoints are accessible

5. **Database connection errors**
   - Solution: Check your database credentials in config
   - Ensure PostgreSQL is running

### Debug Mode

Enable debug logging in `discussion_api.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Database Indexes

All necessary indexes are created by the schema. For large deployments, consider:

```sql
-- Add composite indexes for common queries
CREATE INDEX idx_threads_book_activity 
ON discussion_threads(book_id, last_activity_at DESC);

CREATE INDEX idx_comments_thread_created 
ON discussion_comments(thread_id, created_at ASC);
```

### Caching

Implement caching for frequently accessed data:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300, key_prefix='book_threads')
def get_book_threads(book_id):
    # Your code here
    pass
```

### Pagination

The system uses pagination by default. Adjust `per_page` values as needed:

```python
# In discussion_api.py
per_page = request.args.get('per_page', 20, type=int)  # Change 20 to your preferred value
```

## Security Considerations

1. **Input Validation**: All user inputs are validated
2. **SQL Injection**: Using SQLAlchemy ORM prevents SQL injection
3. **XSS Protection**: HTML is escaped in templates
4. **CSRF Protection**: Use Flask-WTF for forms
5. **Authentication**: All write operations require login
6. **Authorization**: Users can only edit/delete their own content

### Additional Security

Add rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: current_user.id)

@discussion_api.route('/threads/<int:thread_id>/comments', methods=['POST'])
@limiter.limit("10 per minute")
def create_comment(thread_id):
    # Your code here
    pass
```

## Future Enhancements

Potential features to add:

- [ ] Email notifications for thread followers
- [ ] Rich text editor for comments (Markdown/WYSIWYG)
- [ ] Image uploads in comments
- [ ] Mention system (@username)
- [ ] Thread categories/tags
- [ ] Best answer marking
- [ ] User badges and achievements
- [ ] Advanced search with filters
- [ ] Export discussions to PDF
- [ ] Real-time updates with WebSockets

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the API documentation
3. Check browser console for errors
4. Review server logs

## License

This discussion forum system is part of your GetMyEBook-Web application and follows the same license.

## Credits

- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Backend**: Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Fonts**: Google Fonts (Inter)

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-23  
**Author**: Discussion Forum System
