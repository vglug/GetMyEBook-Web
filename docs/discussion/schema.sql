-- Discussion Forum Database Schema for PostgreSQL
-- This schema integrates with your existing books and users tables

-- ============================================
-- 1. Discussion Threads Table
-- ============================================
CREATE TABLE IF NOT EXISTS discussion_threads (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    view_count BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to books table
    CONSTRAINT fk_thread_book FOREIGN KEY (book_id) 
        REFERENCES books(id) ON DELETE CASCADE,
    
    -- Index for better query performance
    CONSTRAINT discussion_threads_book_id_idx 
        CHECK (book_id > 0)
);

-- Indexes for performance
CREATE INDEX idx_discussion_threads_book_id ON discussion_threads(book_id);
CREATE INDEX idx_discussion_threads_user_id ON discussion_threads(user_id);
CREATE INDEX idx_discussion_threads_created_at ON discussion_threads(created_at DESC);
CREATE INDEX idx_discussion_threads_last_activity ON discussion_threads(last_activity_at DESC);

-- ============================================
-- 2. Discussion Comments/Replies Table
-- ============================================
CREATE TABLE IF NOT EXISTS discussion_comments (
    id BIGSERIAL PRIMARY KEY,
    thread_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    parent_comment_id BIGINT DEFAULT NULL,  -- For nested replies
    content TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to discussion_threads
    CONSTRAINT fk_comment_thread FOREIGN KEY (thread_id) 
        REFERENCES discussion_threads(id) ON DELETE CASCADE,
    
    -- Foreign key for nested replies (self-referencing)
    CONSTRAINT fk_comment_parent FOREIGN KEY (parent_comment_id) 
        REFERENCES discussion_comments(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_discussion_comments_thread_id ON discussion_comments(thread_id);
CREATE INDEX idx_discussion_comments_user_id ON discussion_comments(user_id);
CREATE INDEX idx_discussion_comments_parent_id ON discussion_comments(parent_comment_id);
CREATE INDEX idx_discussion_comments_created_at ON discussion_comments(created_at ASC);

-- ============================================
-- 3. Comment Likes/Reactions Table
-- ============================================
CREATE TABLE IF NOT EXISTS discussion_comment_likes (
    id BIGSERIAL PRIMARY KEY,
    comment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reaction_type VARCHAR(20) DEFAULT 'like',  -- like, helpful, insightful, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to discussion_comments
    CONSTRAINT fk_like_comment FOREIGN KEY (comment_id) 
        REFERENCES discussion_comments(id) ON DELETE CASCADE,
    
    -- Ensure one user can only react once per comment with same type
    CONSTRAINT unique_user_comment_reaction 
        UNIQUE (comment_id, user_id, reaction_type)
);

-- Indexes for performance
CREATE INDEX idx_discussion_likes_comment_id ON discussion_comment_likes(comment_id);
CREATE INDEX idx_discussion_likes_user_id ON discussion_comment_likes(user_id);

-- ============================================
-- 4. Thread Followers/Subscriptions Table
-- ============================================
CREATE TABLE IF NOT EXISTS discussion_thread_followers (
    id BIGSERIAL PRIMARY KEY,
    thread_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    notify_on_reply BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to discussion_threads
    CONSTRAINT fk_follower_thread FOREIGN KEY (thread_id) 
        REFERENCES discussion_threads(id) ON DELETE CASCADE,
    
    -- Ensure one user can only follow a thread once
    CONSTRAINT unique_user_thread_follow 
        UNIQUE (thread_id, user_id)
);

-- Indexes for performance
CREATE INDEX idx_discussion_followers_thread_id ON discussion_thread_followers(thread_id);
CREATE INDEX idx_discussion_followers_user_id ON discussion_thread_followers(user_id);

-- ============================================
-- 5. Reported Content Table (Moderation)
-- ============================================
CREATE TABLE IF NOT EXISTS discussion_reports (
    id BIGSERIAL PRIMARY KEY,
    reporter_user_id BIGINT NOT NULL,
    content_type VARCHAR(20) NOT NULL,  -- 'thread' or 'comment'
    content_id BIGINT NOT NULL,
    reason VARCHAR(50) NOT NULL,  -- spam, offensive, inappropriate, etc.
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reviewed, resolved, dismissed
    reviewed_by_user_id BIGINT DEFAULT NULL,
    reviewed_at TIMESTAMP DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_discussion_reports_status ON discussion_reports(status);
CREATE INDEX idx_discussion_reports_content ON discussion_reports(content_type, content_id);

-- ============================================
-- 6. User Reputation/Points Table (Optional)
-- ============================================
CREATE TABLE IF NOT EXISTS discussion_user_reputation (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    total_points BIGINT DEFAULT 0,
    threads_created BIGINT DEFAULT 0,
    comments_posted BIGINT DEFAULT 0,
    helpful_votes_received BIGINT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX idx_discussion_reputation_user_id ON discussion_user_reputation(user_id);
CREATE INDEX idx_discussion_reputation_points ON discussion_user_reputation(total_points DESC);

-- ============================================
-- 7. Triggers for automatic updates
-- ============================================

-- Trigger to update thread's last_activity_at when a new comment is added
CREATE OR REPLACE FUNCTION update_thread_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE discussion_threads 
    SET last_activity_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.thread_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_thread_activity
AFTER INSERT ON discussion_comments
FOR EACH ROW
EXECUTE FUNCTION update_thread_activity();

-- Trigger to update user reputation when they create a thread
CREATE OR REPLACE FUNCTION update_reputation_on_thread()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO discussion_user_reputation (user_id, threads_created, total_points)
    VALUES (NEW.user_id, 1, 5)
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        threads_created = discussion_user_reputation.threads_created + 1,
        total_points = discussion_user_reputation.total_points + 5,
        updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_reputation_on_thread
AFTER INSERT ON discussion_threads
FOR EACH ROW
EXECUTE FUNCTION update_reputation_on_thread();

-- Trigger to update user reputation when they post a comment
CREATE OR REPLACE FUNCTION update_reputation_on_comment()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO discussion_user_reputation (user_id, comments_posted, total_points)
    VALUES (NEW.user_id, 1, 2)
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        comments_posted = discussion_user_reputation.comments_posted + 1,
        total_points = discussion_user_reputation.total_points + 2,
        updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_reputation_on_comment
AFTER INSERT ON discussion_comments
FOR EACH ROW
EXECUTE FUNCTION update_reputation_on_comment();

-- ============================================
-- 8. Views for common queries
-- ============================================

-- View to get thread statistics
CREATE OR REPLACE VIEW discussion_thread_stats AS
SELECT 
    dt.id as thread_id,
    dt.book_id,
    dt.title,
    dt.user_id as author_id,
    dt.created_at,
    dt.last_activity_at,
    dt.view_count,
    dt.is_pinned,
    dt.is_locked,
    COUNT(DISTINCT dc.id) as comment_count,
    COUNT(DISTINCT dtf.id) as follower_count
FROM discussion_threads dt
LEFT JOIN discussion_comments dc ON dt.id = dc.thread_id
LEFT JOIN discussion_thread_followers dtf ON dt.id = dtf.thread_id
GROUP BY dt.id;

-- View to get comment statistics with likes
CREATE OR REPLACE VIEW discussion_comment_stats AS
SELECT 
    dc.id as comment_id,
    dc.thread_id,
    dc.user_id,
    dc.content,
    dc.created_at,
    dc.is_edited,
    COUNT(DISTINCT dcl.id) as like_count,
    COUNT(DISTINCT replies.id) as reply_count
FROM discussion_comments dc
LEFT JOIN discussion_comment_likes dcl ON dc.id = dcl.comment_id
LEFT JOIN discussion_comments replies ON dc.id = replies.parent_comment_id
GROUP BY dc.id;

-- ============================================
-- Comments and Documentation
-- ============================================

COMMENT ON TABLE discussion_threads IS 'Main discussion threads for each book';
COMMENT ON TABLE discussion_comments IS 'Comments and replies within discussion threads';
COMMENT ON TABLE discussion_comment_likes IS 'User reactions/likes on comments';
COMMENT ON TABLE discussion_thread_followers IS 'Users following specific discussion threads';
COMMENT ON TABLE discussion_reports IS 'Reported content for moderation';
COMMENT ON TABLE discussion_user_reputation IS 'User reputation and activity statistics';

COMMENT ON COLUMN discussion_threads.is_pinned IS 'Pinned threads appear at the top';
COMMENT ON COLUMN discussion_threads.is_locked IS 'Locked threads cannot receive new comments';
COMMENT ON COLUMN discussion_comments.parent_comment_id IS 'NULL for top-level comments, references parent for replies';
COMMENT ON COLUMN discussion_comment_likes.reaction_type IS 'Type of reaction: like, helpful, insightful, etc.';
