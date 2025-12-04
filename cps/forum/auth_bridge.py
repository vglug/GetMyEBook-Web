"""
Authentication Bridge between Calibre-Web Users and Forum Users
Provides Single Sign-On (SSO) functionality
"""
from flask_login import current_user
from cps import ub
from cps.forum import db
from werkzeug.security import generate_password_hash
import logging

log = logging.getLogger('cps.forum.auth_bridge')

def get_forum_user_model():
    """Lazy import to avoid circular dependencies"""
    from cps.forum.database.models.user import User as ForumUser
    return ForumUser

def get_or_create_forum_user():
    """
    Get or create forum user for currently logged-in Calibre user
    Provides automatic Single Sign-On functionality
    
    Returns:
        ForumUser: Forum user object or None if not authenticated
    """
    if not current_user.is_authenticated:
        log.debug("User not authenticated, returning None")
        return None
    
    ForumUser = get_forum_user_model()
    
    try:
        # Try to find existing forum user by email
        forum_user = ForumUser.query.filter_by(
            email=current_user.email if current_user.email else f"user_{current_user.id}@local"
        ).first()
        
        if forum_user:
            log.debug(f"Found existing forum user: {forum_user.username}")
            return forum_user
        
        # Create new forum user from Calibre user
        username = current_user.name if hasattr(current_user, 'name') else f"user_{current_user.id}"
        email = current_user.email if current_user.email else f"user_{current_user.id}@local"
        
        log.info(f"Creating new forum user for Calibre user: {username}")
        
        forum_user = ForumUser(
            username=username,
            email=email,
            password=current_user.password if hasattr(current_user, 'password') else generate_password_hash('synced'),
            is_verified=True,  # Auto-verify since they're logged into Calibre
        )
        
        db.session.add(forum_user)
        db.session.commit()
        
        log.info(f"✅ Successfully created forum user  for {username}")
        return forum_user
        
    except Exception as e:
        log.error(f"❌ Error in get_or_create_forum_user: {e}")
        db.session.rollback()
        return None

def sync_calibre_user_to_forum(calibre_user=None):
    """
    Sync a specific Calibre user to forum database
    Used for bulk syncing or manual user creation
    
    Args:
        calibre_user: Calibre User object (defaults to current_user)
    
    Returns:
        ForumUser: Synced forum user object
    """
    if calibre_user is None:
        if not current_user.is_authenticated:
            log.warning("Cannot sync: No user authenticated")
            return None
        calibre_user = current_user
    
    ForumUser = get_forum_user_model()
    
    try:
        email = calibre_user.email if calibre_user.email else f"user_{calibre_user.id}@local"
        
        # Check if forum user exists
        forum_user = ForumUser.query.filter_by(email=email).first()
        
        if forum_user:
            # Update existing user
            forum_user.username = calibre_user.name if hasattr(calibre_user, 'name') else forum_user.username
            forum_user.email = email
            log.info(f"Updated existing forum user: {forum_user.username}")
        else:
            # Create new user
            forum_user = ForumUser(
                username=calibre_user.name if hasattr(calibre_user, 'name') else f"user_{calibre_user.id}",
                email=email,
                password=calibre_user.password if hasattr(calibre_user, 'password') else generate_password_hash('synced'),
                is_verified=True
            )
            db.session.add(forum_user)
            log.info(f"Created new forum user: {forum_user.username}")
        
        db.session.commit()
        return forum_user
        
    except Exception as e:
        log.error(f"❌ Error syncing user to forum: {e}")
        db.session.rollback()
        return None

def bulk_sync_all_users():
    """
    Sync all Calibre users to forum database
    Useful for initial migration or bulk updates
    
    Returns:
        tuple: (success_count, error_count)
    """
    log.info("Starting bulk user sync...")
    
    try:
        # Get all Calibre users
        from cps import ub
        calibre_users = ub.session.query(ub.User).all()
        
        success_count = 0
        error_count = 0
        
        for calibre_user in calibre_users:
            try:
                result = sync_calibre_user_to_forum(calibre_user)
                if result:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                log.error(f"Error syncing user {calibre_user.name}: {e}")
                error_count += 1
        
        log.info(f"✅ Bulk sync complete: {success_count} successful, {error_count} errors")
        return (success_count, error_count)
        
    except Exception as e:
        log.error(f"❌ Bulk sync failed: {e}")
        return (0, -1)

def get_forum_user_id():
    """
    Get forum user ID for current Calibre user
    Helper function for templates and routes
    
    Returns:
        int: Forum user ID or None
    """
    forum_user = get_or_create_forum_user()
    return forum_user.id if forum_user else None

__all__ = [
    'get_or_create_forum_user',
    'sync_calibre_user_to_forum',
    'bulk_sync_all_users',
    'get_forum_user_id'
]
