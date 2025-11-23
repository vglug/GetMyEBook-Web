# Discussion Forum - Integration Examples

## Example 1: Adding Discussion Tab to Book Detail Page

### Option A: Bootstrap Tabs Integration

```html
<!-- In your book detail template (e.g., cps/templates/detail.html) -->

<ul class="nav nav-tabs" id="bookTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="details-tab" data-bs-toggle="tab" 
                data-bs-target="#details" type="button">
            <i class="bi bi-info-circle"></i> Details
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="discussion-tab" data-bs-toggle="tab" 
                data-bs-target="#discussion" type="button">
            <i class="bi bi-chat-dots"></i> Discussion
        </button>
    </li>
</ul>

<div class="tab-content" id="bookTabContent">
    <div class="tab-pane fade show active" id="details">
        <!-- Your existing book details -->
    </div>
    <div class="tab-pane fade" id="discussion">
        <!-- Discussion iframe or embedded content -->
        <iframe src="{{ url_for('discussion.book_discussion', book_id=book.id) }}" 
                style="width:100%; height:800px; border:none;"></iframe>
    </div>
</div>
```

### Option B: Direct Link Button

```html
<!-- Simple button approach -->
<div class="book-actions">
    <a href="{{ url_for('discussion.book_discussion', book_id=book.id) }}" 
       class="btn btn-primary btn-lg">
        <i class="bi bi-chat-dots-fill"></i> Join Discussion
        <span class="badge bg-light text-dark ms-2" id="discussion-count-{{ book.id }}">
            Loading...
        </span>
    </a>
</div>

<script>
// Load discussion count dynamically
fetch('/api/discussion/books/{{ book.id }}/threads')
    .then(res => res.json())
    .then(data => {
        document.getElementById('discussion-count-{{ book.id }}').textContent = 
            data.total + ' discussions';
    });
</script>
```

### Option C: Embedded Widget

```html
<!-- Compact discussion widget -->
<div class="discussion-widget card">
    <div class="card-header bg-primary text-white">
        <h5><i class="bi bi-chat-dots"></i> Recent Discussions</h5>
    </div>
    <div class="card-body" id="recent-discussions-{{ book.id }}">
        <div class="text-center">
            <div class="spinner-border" role="status"></div>
        </div>
    </div>
    <div class="card-footer">
        <a href="{{ url_for('discussion.book_discussion', book_id=book.id) }}" 
           class="btn btn-sm btn-outline-primary w-100">
            View All Discussions
        </a>
    </div>
</div>

<script>
// Load recent discussions
fetch('/api/discussion/books/{{ book.id }}/threads?per_page=3')
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById('recent-discussions-{{ book.id }}');
        if (data.threads && data.threads.length > 0) {
            container.innerHTML = data.threads.map(thread => `
                <div class="mb-2">
                    <a href="/discussion/thread/${thread.id}" class="text-decoration-none">
                        <strong>${thread.title}</strong>
                    </a>
                    <small class="text-muted d-block">
                        ${thread.comment_count} comments • ${thread.view_count} views
                    </small>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p class="text-muted">No discussions yet. Be the first!</p>';
        }
    });
</script>
```

---

## Example 2: Navigation Menu Integration

```html
<!-- In your main navigation (e.g., cps/templates/base.html) -->

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="/">GetMyEBook</a>
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('web.index') }}">
                        <i class="bi bi-house"></i> Home
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('web.books_list') }}">
                        <i class="bi bi-book"></i> Books
                    </a>
                </li>
                
                <!-- Discussion Menu Items -->
                {% if current_user.is_authenticated %}
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="discussionDropdown" 
                       data-bs-toggle="dropdown">
                        <i class="bi bi-chat-dots"></i> Discussions
                    </a>
                    <ul class="dropdown-menu">
                        <li>
                            <a class="dropdown-item" href="{{ url_for('discussion.my_discussions') }}">
                                <i class="bi bi-person-circle"></i> My Discussions
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item" href="{{ url_for('discussion.following_discussions') }}">
                                <i class="bi bi-bookmark"></i> Following
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <a class="dropdown-item" href="/api/discussion/users/{{ current_user.id }}/reputation">
                                <i class="bi bi-trophy"></i> My Reputation
                            </a>
                        </li>
                    </ul>
                </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
```

---

## Example 3: User Profile Integration

```html
<!-- Show user's discussion activity on their profile page -->

<div class="user-discussions">
    <h3>Discussion Activity</h3>
    
    <div class="row">
        <div class="col-md-4">
            <div class="stat-card">
                <h4 id="user-threads-count">-</h4>
                <p>Discussions Started</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card">
                <h4 id="user-comments-count">-</h4>
                <p>Comments Posted</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="stat-card">
                <h4 id="user-reputation-points">-</h4>
                <p>Reputation Points</p>
            </div>
        </div>
    </div>
    
    <h4 class="mt-4">Recent Discussions</h4>
    <div id="user-recent-threads"></div>
</div>

<script>
const userId = {{ user.id }};

// Load user reputation
fetch(`/api/discussion/users/${userId}/reputation`)
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('user-threads-count').textContent = 
                data.reputation.threads_created;
            document.getElementById('user-comments-count').textContent = 
                data.reputation.comments_posted;
            document.getElementById('user-reputation-points').textContent = 
                data.reputation.total_points;
        }
    });

// Load recent threads (you'll need to add this endpoint)
// Or query directly from database
</script>
```

---

## Example 4: Admin Dashboard Integration

```html
<!-- Admin moderation panel -->

<div class="admin-discussion-panel">
    <h2>Discussion Moderation</h2>
    
    <ul class="nav nav-pills mb-3">
        <li class="nav-item">
            <a class="nav-link active" data-bs-toggle="pill" href="#pending-reports">
                Pending Reports <span class="badge bg-danger" id="pending-count">0</span>
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="pill" href="#recent-threads">
                Recent Threads
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="pill" href="#top-users">
                Top Contributors
            </a>
        </li>
    </ul>
    
    <div class="tab-content">
        <div class="tab-pane fade show active" id="pending-reports">
            <!-- Reports list -->
            <div id="reports-list"></div>
        </div>
        <div class="tab-pane fade" id="recent-threads">
            <!-- Recent threads -->
        </div>
        <div class="tab-pane fade" id="top-users">
            <!-- Top users by reputation -->
        </div>
    </div>
</div>

<script>
// Load pending reports (you'll need to add admin endpoints)
// This is a placeholder - implement according to your needs
</script>
```

---

## Example 5: Search Integration

```html
<!-- Add discussion search to your main search -->

<form class="search-form" id="globalSearch">
    <input type="text" class="form-control" id="searchQuery" 
           placeholder="Search books and discussions...">
    <div class="form-check">
        <input class="form-check-input" type="checkbox" id="searchDiscussions">
        <label class="form-check-label" for="searchDiscussions">
            Include discussions
        </label>
    </div>
    <button type="submit" class="btn btn-primary">Search</button>
</form>

<div id="searchResults"></div>

<script>
document.getElementById('globalSearch').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('searchQuery').value;
    const includeDiscussions = document.getElementById('searchDiscussions').checked;
    
    // Search books (your existing search)
    // ...
    
    // Search discussions if checkbox is checked
    if (includeDiscussions) {
        const response = await fetch(`/api/discussion/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            const discussionResults = data.results.map(thread => `
                <div class="search-result">
                    <h5>
                        <i class="bi bi-chat-dots"></i>
                        <a href="/discussion/thread/${thread.id}">${thread.title}</a>
                    </h5>
                    <p>${thread.content.substring(0, 150)}...</p>
                    <small class="text-muted">
                        ${thread.comment_count} comments • ${thread.view_count} views
                    </small>
                </div>
            `).join('');
            
            document.getElementById('searchResults').innerHTML += `
                <h4>Discussions</h4>
                ${discussionResults}
            `;
        }
    }
});
</script>
```

---

## Example 6: Notification System

```python
# In cps/discussion_api.py - Add notification function

from flask_mail import Message, Mail

mail = Mail(app)

def send_discussion_notification(user_id, thread, comment):
    """Send email notification for new comment"""
    # Get user email from database
    user = User.query.get(user_id)
    
    if not user or not user.email:
        return
    
    msg = Message(
        subject=f'New comment on: {thread.title}',
        recipients=[user.email],
        html=f'''
        <h2>New Comment on Discussion</h2>
        <p>Someone commented on a discussion you're following:</p>
        <h3>{thread.title}</h3>
        <blockquote>{comment.content}</blockquote>
        <p>
            <a href="{url_for('discussion.view_thread', thread_id=thread.id, _external=True)}">
                View Discussion
            </a>
        </p>
        '''
    )
    
    mail.send(msg)

# Use in create_comment function:
@discussion_api.route('/threads/<int:thread_id>/comments', methods=['POST'])
@login_required
def create_comment(thread_id):
    # ... existing code ...
    
    # After creating comment, notify followers
    followers = DiscussionThreadFollower.query.filter_by(
        thread_id=thread_id,
        notify_on_reply=True
    ).all()
    
    for follower in followers:
        if follower.user_id != current_user.id:
            send_discussion_notification(follower.user_id, thread, comment)
    
    # ... rest of code ...
```

---

## Example 7: Real-time Updates with WebSockets

```python
# Install flask-socketio
# pip install flask-socketio

from flask_socketio import SocketIO, emit, join_room

socketio = SocketIO(app)

@socketio.on('join_thread')
def on_join(data):
    thread_id = data['thread_id']
    join_room(f'thread_{thread_id}')
    emit('user_joined', {'message': 'You joined the discussion'})

@socketio.on('new_comment')
def on_new_comment(data):
    thread_id = data['thread_id']
    # Broadcast to all users in this thread room
    emit('comment_added', data, room=f'thread_{thread_id}')
```

```html
<!-- In your template -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
const socket = io();
const threadId = {{ thread.id }};

// Join thread room
socket.emit('join_thread', {thread_id: threadId});

// Listen for new comments
socket.on('comment_added', function(data) {
    // Add comment to page without refresh
    const commentHtml = createCommentCard(data.comment);
    document.getElementById('commentsList').insertAdjacentHTML('beforeend', commentHtml);
});

// When posting a comment
function postComment() {
    // ... your existing code ...
    
    // Emit to other users
    socket.emit('new_comment', {
        thread_id: threadId,
        comment: commentData
    });
}
</script>
```

---

## Example 8: Custom Styling

```css
/* Custom theme for discussion forum */
/* Add to your main CSS file */

.discussion-container {
    /* Override default styles */
    --primary-color: #your-brand-color;
    --secondary-color: #your-accent-color;
}

/* Custom thread card style */
.thread-card {
    border-left: 4px solid var(--primary-color);
    transition: all 0.3s ease;
}

.thread-card:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Custom avatar style */
.avatar {
    background: linear-gradient(135deg, #your-color-1, #your-color-2);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .discussion-container {
        background: #1a1a1a;
        color: #e5e5e5;
    }
    
    .thread-card {
        background: #2a2a2a;
        border-color: var(--primary-color);
    }
}
```

---

## Example 9: Analytics Integration

```javascript
// Track discussion engagement with Google Analytics

// Track thread views
gtag('event', 'view_thread', {
    'event_category': 'Discussion',
    'event_label': threadTitle,
    'value': threadId
});

// Track comment posts
gtag('event', 'post_comment', {
    'event_category': 'Discussion',
    'event_label': 'New Comment',
    'value': threadId
});

// Track likes
gtag('event', 'like_comment', {
    'event_category': 'Discussion',
    'event_label': 'Comment Like',
    'value': commentId
});
```

---

## Example 10: Mobile App Integration (API)

```javascript
// React Native / Mobile App Example

// Fetch discussions
const fetchDiscussions = async (bookId) => {
    try {
        const response = await fetch(
            `https://your-domain.com/api/discussion/books/${bookId}/threads`,
            {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            }
        );
        const data = await response.json();
        return data.threads;
    } catch (error) {
        console.error('Error fetching discussions:', error);
    }
};

// Post comment
const postComment = async (threadId, content) => {
    try {
        const response = await fetch(
            `https://your-domain.com/api/discussion/threads/${threadId}/comments`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({ content })
            }
        );
        return await response.json();
    } catch (error) {
        console.error('Error posting comment:', error);
    }
};
```

---

These examples should cover most integration scenarios. Choose the ones that fit your needs and customize as necessary!
