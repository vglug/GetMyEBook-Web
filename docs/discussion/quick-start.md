# Discussion Forum - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Run the Setup Script
```bash
cd /Users/vijisulochana/Documents/GetMyEBook-Web
./setup_discussion_forum.sh
```

### Step 2: Register Blueprints

Add to `cps/__init__.py` (around line 50-60, after other imports):

```python
# Import discussion forum blueprints
from cps.discussion_api import discussion_api
from cps.discussion_routes import discussion_routes

# Register blueprints (add after other blueprint registrations)
app.register_blueprint(discussion_api)
app.register_blueprint(discussion_routes)
```

### Step 3: Add Discussion Tab to Book Pages

Find your book detail template (likely `cps/templates/detail.html`) and add:

```html
<!-- Add to your book detail page tabs or buttons -->
<a href="{{ url_for('discussion.book_discussion', book_id=book.id) }}" 
   class="btn btn-primary">
    <i class="bi bi-chat-dots"></i> Discussion
</a>
```

### Step 4: Restart Your App
```bash
# Stop your current Flask app (Ctrl+C)
# Then restart it
python cps.py
```

### Step 5: Test It!
Navigate to: `http://localhost:8083/discussion/book/1`

---

## 📋 API Quick Reference

### Get Discussions
```javascript
// Get all threads for a book
fetch('/api/discussion/books/1/threads?sort=recent')
  .then(res => res.json())
  .then(data => console.log(data.threads));
```

### Create Thread
```javascript
// Create new discussion
fetch('/api/discussion/books/1/threads', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    title: 'Great book!',
    content: 'I really enjoyed this book because...'
  })
}).then(res => res.json());
```

### Add Comment
```javascript
// Post a comment
fetch('/api/discussion/threads/1/comments', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    content: 'I agree with your points!'
  })
}).then(res => res.json());
```

### Like Comment
```javascript
// Like/unlike a comment
fetch('/api/discussion/comments/1/like', {
  method: 'POST'
}).then(res => res.json());
```

---

## 🎨 Customization Examples

### Change Color Scheme

In `discussion_forum.html` and `discussion_thread.html`, modify the CSS variables:

```css
:root {
    --primary-color: #6366f1;     /* Change to your brand color */
    --secondary-color: #8b5cf6;   /* Change to your accent color */
    --success-color: #10b981;
    --danger-color: #ef4444;
}
```

### Modify Reputation Points

In `discussion_forum_schema.sql`, find the triggers and change point values:

```sql
-- Thread creation points (default: 5)
total_points = discussion_user_reputation.total_points + 10

-- Comment posting points (default: 2)
total_points = discussion_user_reputation.total_points + 3
```

### Add Custom Badges

In `discussion_models.py`, add a method to the `DiscussionUserReputation` class:

```python
def get_badge(self):
    if self.total_points >= 1000:
        return "Expert"
    elif self.total_points >= 500:
        return "Advanced"
    elif self.total_points >= 100:
        return "Contributor"
    else:
        return "Beginner"
```

---

## 🔧 Common Customizations

### 1. Add Rich Text Editor

Replace the textarea with a WYSIWYG editor:

```html
<!-- Add to your template -->
<link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
<script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>

<div id="editor"></div>

<script>
var quill = new Quill('#editor', {
  theme: 'snow'
});
</script>
```

### 2. Add Email Notifications

In `discussion_api.py`, after creating a comment:

```python
# Send email to thread followers
followers = DiscussionThreadFollower.query.filter_by(
    thread_id=thread_id,
    notify_on_reply=True
).all()

for follower in followers:
    if follower.user_id != current_user.id:
        send_notification_email(follower.user_id, thread, comment)
```

### 3. Add Markdown Support

Install markdown library:
```bash
pip install markdown
```

In your template:
```python
from markdown import markdown

# In your route
thread.content_html = markdown(thread.content)
```

### 4. Add User Avatars

Integrate with Gravatar:

```html
<!-- In your template -->
<img src="https://www.gravatar.com/avatar/{{ user.email|md5 }}?d=identicon" 
     class="avatar" alt="Avatar">
```

---

## 📊 Database Queries Examples

### Get Most Active Users
```sql
SELECT user_id, total_points, threads_created, comments_posted
FROM discussion_user_reputation
ORDER BY total_points DESC
LIMIT 10;
```

### Get Most Popular Threads
```sql
SELECT dt.*, COUNT(dc.id) as comment_count
FROM discussion_threads dt
LEFT JOIN discussion_comments dc ON dt.id = dc.thread_id
GROUP BY dt.id
ORDER BY comment_count DESC, dt.view_count DESC
LIMIT 10;
```

### Get Recent Activity
```sql
SELECT dt.title, dc.content, dc.created_at
FROM discussion_comments dc
JOIN discussion_threads dt ON dc.thread_id = dt.id
ORDER BY dc.created_at DESC
LIMIT 20;
```

---

## 🐛 Troubleshooting

### Issue: "Blueprint not found"
**Solution**: Make sure you imported and registered the blueprints in your main app file.

### Issue: "Table doesn't exist"
**Solution**: Run the SQL schema file:
```bash
psql -U vglug -d your_db -f discussion_forum_schema.sql
```

### Issue: "Comments not loading"
**Solution**: Check browser console for errors. Verify the API endpoint is accessible:
```bash
curl http://localhost:8083/api/discussion/books/1/threads
```

### Issue: "Permission denied"
**Solution**: Make sure user is logged in. Check Flask-Login configuration.

---

## 📱 Mobile Optimization

The templates are already mobile-responsive, but you can enhance them:

```css
/* Add to your custom CSS */
@media (max-width: 576px) {
    .thread-title {
        font-size: 1.2rem;
    }
    
    .comment-card.reply {
        margin-left: 15px;
    }
}
```

---

## 🔐 Security Checklist

- [x] SQL Injection protection (SQLAlchemy ORM)
- [x] XSS protection (Template escaping)
- [x] Authentication required for posting
- [x] Authorization checks for edit/delete
- [ ] Add CSRF protection (recommended)
- [ ] Add rate limiting (recommended)
- [ ] Add content moderation (optional)

### Add CSRF Protection

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# In your forms
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Add Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: current_user.id,
    default_limits=["200 per day", "50 per hour"]
)

@limiter.limit("10 per minute")
@discussion_api.route('/threads/<int:thread_id>/comments', methods=['POST'])
def create_comment(thread_id):
    # Your code
    pass
```

---

## 📈 Performance Tips

1. **Enable Caching**
   ```python
   from flask_caching import Cache
   cache = Cache(app, config={'CACHE_TYPE': 'redis'})
   ```

2. **Add Database Indexes**
   ```sql
   CREATE INDEX idx_custom ON discussion_threads(book_id, last_activity_at DESC);
   ```

3. **Lazy Load Comments**
   - Load only top-level comments initially
   - Load replies on demand

4. **Use CDN for Assets**
   - Bootstrap, icons, fonts from CDN
   - Reduces server load

---

## 🎯 Next Steps

1. ✅ Complete basic setup
2. ✅ Test all features
3. 🔲 Customize colors and branding
4. 🔲 Add email notifications
5. 🔲 Implement moderation tools
6. 🔲 Add analytics tracking
7. 🔲 Create admin dashboard

---

## 📞 Support

For detailed documentation, see: `DISCUSSION_FORUM_GUIDE.md`

For issues:
1. Check browser console
2. Check server logs
3. Review API responses
4. Check database connections

---

**Happy Coding! 🚀**
