<template>
    <div class="comment-item d-flex mb-4 mt-1" :class="{'nested-reply': isReply}">
        <div class="flex-shrink-0 mr-3 comment-icon">
            <img :src="comment.owner.profile_picture" class="rounded-circle" :width="isReply ? 28 : 36" :height="isReply ? 28 : 36" style="object-fit: cover;">
        </div>
        <div class="flex-grow-1">
            <div class="d-flex align-items-baseline mb-1">
                <h6 class="font-weight-bold m-0 mr-2" style="font-size: 0.95rem;">
                    {{ comment.owner.name }}
                </h6>
                <span class="text-muted" style="font-size: 0.8rem;">
                    {{ postedAt }} 
                    <span class="mx-1">&bull;</span>
                    {{ messageTime }}
                </span>
                 <!-- Push to right end -->
                <div class="position-relative ml-auto">
                    <span class="three-btn" @click="toggleMenu">
                        <i class="fa-solid fa-ellipsis-vertical"></i>
                    </span>
                    <div v-if="showMenu" class="dropdown-menu dropdown-menu-right show shadow-sm" style="top: 100%; right: 0; min-width: 120px; z-index: 1000; position: absolute;">
                        <template v-if="isOwner || isAdmin">
                            <button class="dropdown-item" @click="showEditionInput">
                                <i class="fas fa-pen mr-2"></i>Edit
                            </button>
                        </template>
                        <template v-if="isOwner || isAdmin">
                            <button class="dropdown-item text-danger" @click="deleteComment">
                                <i class="fas fa-trash mr-2"></i>Delete
                            </button>
                        </template>
                    </div>
                </div>
                <!-- Backbone for closing menu on outside click -->
                <div v-if="showMenu" @click="showMenu = false" class="fixed-inset" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 999; cursor: default;"></div>
            </div>
            
            <div class="comment-body">
                <textarea v-model="content" class="form-control mb-2" v-if="editing" rows="3"></textarea>
                <div v-else class="text-dark" style="font-size: 0.95rem; line-height: 1.5;" v-html="formattedContent">
                </div>
            </div>
            <div class="comment-actions mt-1 d-flex align-items-center"> 
                <div class="d-flex align-items-center mr-3">
                    <div class="like-wrapper d-flex align-items-center">
                        <div class="reaction-box">
                            <span class="reaction-icon" @click.stop="triggerReaction('like')" title="Like">👍</span>
                            <span class="reaction-icon" @click.stop="triggerReaction('celebrate')" title="Celebrate">👏</span>
                            <span class="reaction-icon" @click.stop="triggerReaction('support')" title="Support">🤝</span>
                            <span class="reaction-icon" @click.stop="triggerReaction('love')" title="Love">❤️</span>
                            <span class="reaction-icon" @click.stop="triggerReaction('insightful')" title="Insightful">💡</span>
                            <span class="reaction-icon" @click.stop="triggerReaction('funny')" title="Funny">😂</span>
                        </div>
                        
                        <button class="like-btn btn-link btn-sm p-0 text-muted font-weight-bold" @click="toggleLike" style="text-decoration: none; font-size: 0.9rem;">
                            <span :class="{'text-primary': liked && reactionType === 'like', 'text-success': liked && reactionType === 'celebrate', 'text-warning': liked && (reactionType === 'support' || reactionType === 'insightful'), 'text-danger': liked && reactionType === 'love', 'text-info': liked && reactionType === 'funny'}">
                                {{ reactionLabel }}
                            </span>
                        </button>
                    </div>

                    <span class="text-muted mx-2">&middot;</span>

                    <!-- Reaction Status (Icons + Count) -->
                    <div v-if="likesCount > 0" class="ml-2 d-flex align-items-center text-muted small" style="cursor: pointer;" @click="toggleLike">
                        <span class="mr-1">&middot;</span>
                        <div class="reaction-stack d-flex align-items-center">
                            <span v-if="liked" class="reaction-mini-icon" :class="reactionType">
                                <i :class="reactionIconClass"></i>
                            </span>
                            <!-- Show top reaction from others if I haven't liked it but others have -->
                            <span v-if="!liked && likesCount > 0 && topReaction" class="reaction-mini-icon" :class="topReaction">
                                <i :class="getIconClass(topReaction)"></i>
                            </span>
                            <!-- Fallback generic like if no top reaction info -->
                            <span v-if="!liked && likesCount > 0 && !topReaction" class="reaction-mini-icon like">
                                <i class="fas fa-thumbs-up"></i>
                            </span>
                            <!-- Stack effect if multiple -->
                            <!-- Stack effect if multiple -->
                            <span v-if="likesCount > 1" class="reaction-mini-icon" :class="topReaction || 'like'" style="margin-left: -6px;">
                                <i :class="getIconClass(topReaction || 'like')"></i>
                            </span>
                        </div>
                        <span class="ml-1">{{ likesCount }}</span>
                    </div>
                </div>
                <!-- Reply button with message icon -->
                    <button class="btn btn-link btn-sm p-0 reply-btn" @click="toggleReply" style="text-decoration: none; font-size: 0.9rem;">
                        <i class="far fa-comment-dots message-icon"></i>
                        <span class="reply-text">Reply</span>
                    </button>
                    
                    <!-- Reply count - clickable to toggle replies -->
                    <button v-if="hasReplies" class="btn btn-link btn-sm p-0 reply-count-btn" @click="toggleRepliesOnly" style="text-decoration: none; font-size: 0.9rem;">
                        <span class="text-muted mx-2">&middot;</span>
                        <span class="reply-count-text">{{ comment.replies.length }} {{ comment.replies.length === 1 ? 'reply' : 'replies' }}</span>
                    </button>
                <template v-if="isOwner || isAdmin">
                     <button class="btn btn-link btn-sm p-0 mr-3 text-primary" v-if="editing" @click="updateComment">
                        <small>Save</small>
                    </button>
                    <button class="btn btn-link btn-sm p-0 text-danger" v-if="editing" @click="hideEditionInput">
                        <small>Cancel</small>
                    </button>
                </template>
            </div>
            
            <!-- Reply Input Section -->
            <!-- Reply Input Section -->
            <div v-if="isReplying" class="reply-container mt-3 d-flex animate-fade-in">
                
                <div v-if="!canReply" class="w-100 login-prompt text-center p-3" style="background: #f8f9fa; border-radius: 12px;">
                     <template v-if="isLoggedIn">
                         <span class="text-secondary"><i class="fas fa-envelope mr-2"></i> Please verify your email to reply.</span>
                     </template>
                     <template v-else>
                         <span class="text-secondary">
                             <a href="/login" class="font-weight-bold text-primary">Login</a> or <a href="/register" class="font-weight-bold text-primary">Sign up</a> to reply
                         </span>
                     </template>
                </div>

                <template v-else>
                    <div class="flex-shrink-0 mr-3">
                         <img :src="comment.owner.profile_picture" class="rounded-circle" width="36" height="36" style="object-fit: cover;">
                    </div>
                    <div class="flex-grow-1">
                        <div class="reply-card">
                             <div class="reply-header mb-2 px-3 pt-3">
                                <span class="font-weight-bold text-dark">{{ currentUserName }}</span>
                             </div>
                             <div class="px-3 pb-2">
                                <textarea 
                                    v-model="replyContent" 
                                    ref="replyInput"
                                    class="form-control border-0 p-0 reply-textarea" 
                                    placeholder="What are your thoughts?" 
                                    rows="2" 
                                ></textarea>
                             </div>
                             <div class="reply-footer d-flex justify-content-between align-items-center px-3 pb-3">
                                  <div class="d-flex text-muted gap-3">
                                      <i class="far fa-face-smile action-icon" title="Emoji"></i>
                                      <i class="far fa-image action-icon" title="Image"></i>
                                  </div>
                                  <button class="btn btn-primary btn-sm rounded-pill px-4 font-weight-bold" @click="submitReply">Reply</button>
                             </div>
                        </div>
                    </div>
                </template>
            </div>
            
            <!-- View Previous Replies Toggle - Now hidden as we use the reply count button instead -->
            <!-- Keeping it for animation purposes if needed -->

            <!-- Recursive Replies with smooth animation -->
            <transition name="replies-expand">
                <div v-if="showReplies && hasReplies" class="replies-wrapper">
                    <Comment 
                        v-for="reply in comment.replies" 
                        :key="reply.id" 
                        :comment="reply" 
                        :users="users"
                        :thread-id="threadId"
                        :is-reply="true"
                        class="nested-reply"
                        @reply="$emit('reply', $event)"
                        @update="$emit('update', $event)"
                        @delete="$emit('delete', $event)"
                    />
                </div>
            </transition>
        </div>
    </div>
</template>

<script>
    import axios from "axios";

    export default {
        name: 'Comment',
        props: [
            'comment',
            'users',
            'isReply',
            'threadId'
        ],
        data() {
            return {
                editing: false,
                showMenu: false,
                content: "",
                liked: false, 
                likesCount: 0,
                reactionType: 'like', // default
                topReaction: null,
                now: new Date(),
                isReplying: false,
                replyContent: "",
                showReplies: false
            }
        },
        mounted() {
            // Debug: Log the full comment object to see what backend is actually sending
            console.log('Comment data:', this.comment);
            console.log('User reaction data check:', {
                current_user_reaction: this.comment.current_user_reaction,
                reaction_type: this.comment.reaction_type,
                user_reaction: this.comment.user_reaction,
                reaction: this.comment.reaction,
                liked_by_current_user: this.comment.liked_by_current_user
            });
            
            if (this.comment.likes_count !== undefined && this.comment.likes_count !== null) {
                this.likesCount = parseInt(this.comment.likes_count);
            }
            
            // First, check if current user has liked this comment
            if (this.comment.liked_by_current_user) {
                this.liked = true; 
                
                // IMPORTANT: Only set reaction type if user has actually liked the comment
                // Check various possible keys that backend might use
                const rType = this.comment.current_user_reaction 
                           || this.comment.reaction_type 
                           || this.comment.user_reaction 
                           || this.comment.reaction;
                
                if (rType && typeof rType === 'string') {
                    this.reactionType = rType;
                    console.log('User reaction type set to:', rType);
                } else {
                    // Default to 'like' if user has liked but no specific type provided
                    this.reactionType = 'like';
                    console.log('User has liked but no specific reaction type found, defaulting to "like"');
                }
            } else {
                // User hasn't liked, keep default 'like' type for when they do
                this.liked = false;
                this.reactionType = 'like';
                console.log('User has not liked this comment');
            }

            if (this.comment.top_reaction) {
                this.topReaction = this.comment.top_reaction;
                console.log('Top reaction from others:', this.topReaction);
            }

            this.timer = setInterval(() => {
                this.now = new Date();
            }, 1000);
        },
        destroyed() {
            clearInterval(this.timer);
        },
        methods: {
            getIconClass(type) {
                const map = {
                    'like': 'fas fa-thumbs-up',
                    'celebrate': 'fas fa-hands-clapping',
                    'support': 'fas fa-hand-holding-heart',
                    'love': 'fas fa-heart',
                    'insightful': 'fas fa-lightbulb',
                    'funny': 'fas fa-face-laugh-squint'
                };
                return map[type] || 'fas fa-thumbs-up';
            },
            triggerReaction(type) {
                console.log('=== Trigger Reaction Called ===');
                console.log('Reaction type:', type);
                console.log('Current liked state:', this.liked);
                console.log('Current reaction type:', this.reactionType);
                
                // If clicking the same reaction type that's already active, do nothing
                if (this.liked && this.reactionType === type) {
                    console.log('Same reaction already active, ignoring');
                    return;
                }

                // Update the reaction type
                const oldReactionType = this.reactionType;
                this.reactionType = type;

                // If not liked yet, toggle like to add reaction
                if (!this.liked) {
                    console.log('Not liked yet, calling toggleLike');
                    this.toggleLike();
                } else {
                    // User is changing from one reaction to another
                    console.log('Changing reaction from', oldReactionType, 'to', type);
                    
                    // Update existing reaction without toggling count
                    // Send to backend with the new reaction type
                    axios.post(this.endpoint() + '/like', { 
                        reaction_type: this.reactionType,
                        type: this.reactionType,
                        reaction: this.reactionType
                    })
                    .then(response => {
                        console.log('Reaction update successful:', response.data);
                    })
                    .catch(e => {
                        console.error('Error updating reaction:', e);
                        // Revert on error
                        this.reactionType = oldReactionType;
                    });
                }
            },
            toggleLike() {
                console.log('=== Toggle Like Called ===');
                console.log('Current liked state BEFORE toggle:', this.liked);
                console.log('Current reaction type:', this.reactionType);
                
                this.liked = !this.liked;
                
                // If unliking, reset type to default for next time
                if(!this.liked) {
                    console.log('Unliking, resetting reaction type to like');
                    this.reactionType = 'like';
                }

                this.likesCount += this.liked ? 1 : -1;
                
                // Send multiple variants to ensure backend compatibility
                const payload = { 
                    reaction_type: this.liked ? this.reactionType : null,
                    type: this.liked ? this.reactionType : null,
                    reaction: this.liked ? this.reactionType : null
                };
                
                console.log('Sending payload to backend:', payload);

                axios.post(this.endpoint() + '/like', payload)
                    .then(response => {
                        console.log('Like/Unlike successful:', response.data);
                    })
                    .catch(e => {
                        console.error('Error toggling like:', e);
                        // Revert on error
                        this.liked = !this.liked;
                        this.likesCount += this.liked ? 1 : -1;
                    });
            },
            escapeHtml(text) {
                const map = {
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#039;'
                };
                return text.replace(/[&<>"']/g, function(m) { return map[m]; });
            },
            escapeRegex(string) {
                return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            },
            endpoint() {
                return `/forum/api/comments/${this.comment.id}`;
            },
            deleteComment() {
                this.showMenu = false;
                if(!confirm("Are you sure you want to delete this comment?")) return;
                axios.delete(this.endpoint())
                    .then(() => {
                        this.$emit('delete', this.comment)
                    })
                    .catch(e => console.log(e))
            },
            showEditionInput() {
                this.showMenu = false;
                this.content = this.comment.content;
                this.editing = true;
            },
            hideEditionInput() {
                this.editing = false;
            },
            updateComment() {
                // optimistic update
                const oldContent = this.comment.content;

                if (oldContent ===  this.content && (this.content.trim().length) === 0 || !this.content.trim()) {
                    this.editing = false;
                    return;
                }
                else {
                    console.log("Old content:", oldContent);
                    console.log("Updating comment to:", this.content);
                    this.$emit('update', { ...this.comment, content: this.content });
                    this.editing = false;
                    axios.patch(this.endpoint(), { content: this.content })
                        .then(({data}) => {
                            this.$emit('update', data)
                        })
                        .catch(error => {
                            // revert
                            this.$emit('update', { ...this.comment, content: oldContent });
                            console.log(error)
                        });
                    }
            },
            toggleMenu() {
                this.showMenu = !this.showMenu;
            },
            toggleReply() {
                this.isReplying = !this.isReplying;
                if (this.isReplying && this.canReply) {
                    this.$nextTick(() => {
                        if(this.$refs.replyInput) this.$refs.replyInput.focus();
                    });
                }
            },
            submitReply() {
                console.log('=== submitReply Called ===');
                if (!this.replyContent.trim()) {
                    console.log('Reply content is empty');
                    return;
                }
                
                // Create nested reply with parent_id
                const threadId = this.threadId || this.comment.thread_id;
                console.log('Thread ID:', threadId);
                console.log('Parent Comment ID:', this.comment.id);

                const payload = {
                    content: this.replyContent,
                    parent_id: this.comment.id  // This comment is the parent
                };
                console.log('Payload:', payload);
                
                const url = `/forum/api/threads/${threadId}/comments`;
                console.log('Posting to URL:', url);
                
                axios.post(url, payload)
                    .then(response => {
                        console.log('Reply created successfully. Response data:', response.data);
                        console.log('Response status:', response.status);
                        
                        // Add the new reply to this comment's replies array
                        if (!this.comment.replies) {
                            console.log('Initializing replies array');
                            this.$set(this.comment, 'replies', []);
                        }
                        this.comment.replies.push(response.data);
                        
                        // Show the replies section
                        console.log('Showing replies section');
                        this.showReplies = true;
                        
                        // Clear and close
                        this.replyContent = "";
                        this.isReplying = false;
                        console.log('isReplying set to false');
                        
                        // Emit to parent for any additional handling
                        this.$emit('reply', response.data);
                    })
                    .catch(error => {
                        console.error('Error creating reply:', error);
                        if (error.response) {
                             console.error('Error Response Data:', error.response.data);
                             console.error('Error Response Status:', error.response.status);
                             console.error('Error Response Headers:', error.response.headers);
                        } else if (error.request) {
                             console.error('Error Request:', error.request);
                        } else {
                             console.error('Error Message:', error.message);
                        }
                        alert('Failed to post reply. Please try again.');
                    });
            },
            // Legacy reply method if used by something else, redirected
            reply() {
                this.toggleReply();
            },
            toggleReplies() {
                this.showReplies = !this.showReplies;
            },
            toggleRepliesOnly() {
                // Only toggle replies visibility, don't open reply input
                this.showReplies = !this.showReplies;
            }
        },
        computed: {
            reactionLabel() {
                if (!this.liked) return 'Like';
                const map = {
                    'like': 'Like',
                    'celebrate': 'Celebrate',
                    'support': 'Support',
                    'love': 'Love',
                    'insightful': 'Insightful',
                    'funny': 'Funny'
                };
                return map[this.reactionType] || 'Like';
            },
            reactionIconClass() {
                const map = {
                    'like': 'fas fa-thumbs-up',
                    'celebrate': 'fas fa-hands-clapping',
                    'support': 'fas fa-hand-holding-heart',
                    'love': 'fas fa-heart',
                    'insightful': 'fas fa-lightbulb',
                    'funny': 'fas fa-face-laugh-squint'
                };
                return map[this.reactionType] || 'fas fa-thumbs-up';
            },
            postedAt() {
                if (!this.comment.created_at) return '';
                
                let dateStr = this.comment.created_at;
                if (typeof dateStr === 'string') {
                     // Standardize format slightly for browser parsing compatibility (replace space with T)
                     // Do NOT force UTC (Z) as server seems to return Local Time relative to server
                     dateStr = dateStr.replace(' ', 'T');
                }
                
                const date = new Date(dateStr);
                const seconds = Math.floor((this.now - date) / 1000);
                
                if (seconds < 0) return "0s";

                let interval = seconds / 31536000;
                if (interval >= 1) return Math.floor(interval) + "y";
                
                interval = seconds / 2592000;
                if (interval >= 1) return Math.floor(interval) + "mo";
                
                interval = seconds / 86400;
                if (interval >= 1) return Math.floor(interval) + "d";
                
                interval = seconds / 3600;
                if (interval >= 1) return Math.floor(interval) + "h";
                
                interval = seconds / 60;
                if (interval >= 1) return Math.floor(interval) + "m";
                
                return Math.floor(seconds) + "s";
            },
            isOwner() {
                return !! window.Auth && window.Auth.id === this.comment.user_id
            },
            isAdmin() {
                return !! window.Auth && window.Auth.isAdmin;
            },
            formattedContent() {
                let content = this.escapeHtml(this.comment.content || "");
                if (!this.users || !this.users.length) return content;
                
                // Sort users by name length desc to prioritize longer names
                const sortedUsers = [...this.users].sort((a, b) => b.name.length - a.name.length);
                
                sortedUsers.forEach(user => {
                    const name = user.name;
                    // Match @Name
                    // strict matching to avoid partial replacements of same name if possible
                    // simple replace for now:
                    const escapedName = this.escapeRegex(name);
                    const regex = new RegExp(`@${escapedName}`, 'g');
                    content = content.replace(regex, `<span class="text-primary font-weight-bold">@${this.escapeHtml(name)}</span>`);
                });
                return content;
            },
            messageTime() {
                if (!this.comment.created_at) return '';
                let dateStr = this.comment.created_at;
                if (typeof dateStr === 'string') dateStr = dateStr.replace(' ', 'T');
                const date = new Date(dateStr);
                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            },
            currentUserAvatar() {
                if (window.Auth && window.Auth.profile_picture) {
                    return window.Auth.profile_picture;
                }
                // Fallback to UI Avatars if user has name but no picture
                if (window.Auth && window.Auth.name) {
                    return `https://ui-avatars.com/api/?name=${encodeURIComponent(window.Auth.name)}&background=random&color=fff`;
                }
                // Generic fallback
                return 'https://www.gravatar.com/avatar/default?d=mp';
            },
            currentUserName() {
                return window.Auth ? window.Auth.name : 'Guest';
            },
            isLoggedIn() {
                return !!window.Auth;
            },
            canReply() {
                return !!window.Auth && window.Auth.email_verified;
            },
            hasReplies() {
                return this.comment.replies && this.comment.replies.length > 0;
            }
        }
    }
</script>

<style scoped>
    .three-btn {
        color: #6c757d !important;
        cursor: pointer;
        padding: 4px 8px;
    }

    .three-btn:hover {
        background-color: #f1f1f1;
        border-radius: 4px;
    }

    .like-btn {
        outline: 0;
        border: none;
        background-color:#FFFFFF;
    }
    /* Comment Item */
    .comment-item {
        transition: background-color 0.2s;
        border-bottom: 1px solid var(--border-color);
    }
    
    /* Remove border for nested replies */
    .comment-item.nested-reply {
        border-bottom: none;
        margin-bottom: 8px !important;
        margin-top: 8px !important;
    }

    .comment-item:last-child {
        border-bottom: none;
    }
    
    /* View Replies Toggle */
    .view-replies-container {
        position: relative;
    }

    .view-replies-line {
        display: flex;
        align-items: center;
        color: #8e8e8e;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        user-select: none;
        margin-left: 2px; /* Align with text */
    }
    
    .line-dashes {
        display: inline-block;
        width: 24px;
        height: 1px;
        background-color: #8e8e8e;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    /* Thread Connection Line */
    .replies-wrapper {
        position: relative;
        border-left: 2px solid #eef0f2; /* Vertical Thread Line */
        margin-left: 12px;
        padding-left: 16px;
    }

    /* Curve the line slightly for the toggle if desired, or keep straight */
    
    .view-replies-line:hover {
        color: #555;
    }
    .view-replies-line:hover .line-dashes {
        background-color: #555;
    }

    .comment-actions {
        transition: opacity 0.2s;
        display: flex;
        gap: 16px;
        padding-bottom: 0.2rem;
    }
    /* Reaction Picker Details */
    .like-wrapper {
        position: relative;
        display: inline-block;
    }

    .reaction-box {
        /* Hidden by default */
        visibility: hidden;
        opacity: 0;
        display: flex; /* Always layout as flex */
        align-items: center;
        
        position: absolute;
        bottom: 100%; /* Align to top of wrapper */
        left: -10px; 
        background-color: white;
        border-radius: 50px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        padding: 8px 16px;
        gap: 12px;
        z-index: 1000;
        margin-bottom: 12px; /* Visual gap */
        white-space: nowrap;
        border: 1px solid rgba(0,0,0,0.05);

        /* Smooth transition for showing/hiding */
        transform: translateY(10px) scale(0.9);
        transition: all 0.2s cubic-bezier(0.18, 0.89, 0.32, 1.28);
        transition-delay: 0.3s; /* Delay hiding to make it forgiving */
        pointer-events: none;
    }

    /* Invisible Bridge to cover the gap between button and box */
    .reaction-box::after {
        content: '';
        position: absolute;
        left: 0;
        width: 100%;
        bottom: -15px; /* Extend downwards to touch the button area */
        height: 20px;
        background: transparent;
    }

    /* Hover State */
    .like-wrapper:hover .reaction-box {
        visibility: visible;
        opacity: 1;
        transform: translateY(0) scale(1);
        transition-delay: 0s; /* Show immediately */
        pointer-events: auto;
    }

    .reaction-icon {
        font-size: 1.6rem;
        cursor: pointer;
        transition: transform 0.2s cubic-bezier(0.18, 0.89, 0.32, 1.28);
        user-select: none;
        line-height: 1;
    }

    .reaction-icon:hover {
        transform: scale(1.35) translateY(-4px);
    }
    
    /* Mini Icons in Status */
    .reaction-mini-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        color: white;
        font-size: 10px;
        border: 2px solid white; /* Overlap effect border */
    }
    
    /* Colors for Mini Icons */
    .reaction-mini-icon.like { background-color: #1b74e4; }
    .reaction-mini-icon.celebrate { background-color: #26a541; }
    .reaction-mini-icon.support { background-color: #7b68ee; }
    .reaction-mini-icon.love { background-color: #f02849; }
    .reaction-mini-icon.insightful { background-color: #e5a50a; }
    .reaction-mini-icon.funny { background-color: #1da1f2; }
/* 📱 Mobile Responsive */
    @media (max-width: 768px) {
        .comment-icon img{
            width: 30px;
            height: 30px;
            margin-top: 30%;
        }
        
        .comment-actions {
            gap: 12px;
        }

        .reply-container .flex-shrink-0 {
            display: none !important; /* Hide avatar in reply box on mobile to save space */
        }
        .reply-container .flex-grow-1 {
            width: 100%;
        }
        .reply-card {
            border-radius: 12px;
        }
    }

    /* Reply Card Styles */
    .reply-card {
        background: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        transition: box-shadow 0.2s;
        position: relative;
    }
    
    .reply-card:focus-within {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-color: #d0d0d0;
    }

    .reply-textarea {
        background: transparent;
        resize: none;
        box-shadow: none !important;
        font-size: 0.95rem;
    }
    .reply-textarea::placeholder {
        color: #888;
    }

    .action-icon {
        font-size: 1.25rem;
        color: #666;
        cursor: pointer;
        transition: color 0.2s;
    }
    .action-icon:hover {
        color: #333;
    }

    .animate-fade-in {
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .gap-3 {
        gap: 1rem;
    }
    
    .login-prompt {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px dashed #dee2e6;
    }
    
    /* Reply Button with Message Icon */
    .reply-btn {
        color: #8e8e8e !important;
        font-weight: 600 !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: color 0.2s ease;
    }
    
    .reply-btn:hover {
        color: #555 !important;
    }
    
    .message-icon {
        font-size: 0.95rem;
        stroke-width: 1.5;
    }
    
    .reply-text {
        font-weight: 600;
    }
    
    /* Reply Count Button */
    .reply-count-btn {
        color: #8e8e8e;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
    }
    
    .reply-count-text {
        font-weight: 600;
        position: relative;
    }
    
    .reply-count-btn:hover .reply-count-text {
        color: #555;
        text-decoration: underline;
    }
    
    /* Smooth Expand/Collapse Animation for Replies */
    .replies-expand-enter-active,
    .replies-expand-leave-active {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    
    .replies-expand-enter {
        max-height: 0;
        opacity: 0;
        transform: translateY(-10px);
    }
    
    .replies-expand-enter-to {
        max-height: 2000px;
        opacity: 1;
        transform: translateY(0);
    }
    
    .replies-expand-leave {
        max-height: 2000px;
        opacity: 1;
        transform: translateY(0);
    }
    
    .replies-expand-leave-to {
        max-height: 0;
        opacity: 0;
        transform: translateY(-10px);
    }
    
    /* Nested Reply Indentation - Desktop */
    .nested-reply {
        padding-left: 0;
        margin-top: 12px;
    }
    
    .replies-wrapper {
        position: relative;
        border-left: 2px solid #eef0f2; /* Vertical Thread Line */
        margin-left: 20px;
        padding-left: 16px;
        margin-top: 12px;
    }
    
    /* Highlight new replies briefly */
    @keyframes highlight {
        0% { background-color: rgba(0, 123, 255, 0.1); }
        100% { background-color: transparent; }
    }
    .new-reply {
        animation: highlight 3s ease-out;
    }

    /* Mobile Touch-Friendly Design - Reduced Indentation */
    @media (max-width: 768px) {
        .replies-wrapper {
            margin-left: 10px;
            padding-left: 10px;
            border-left-width: 2px;
        }
        
        .comment-icon img {
            width: 28px !important;
            height: 28px !important;
        }
        
        .reply-btn,
        .reply-count-btn {
            padding: 4px 8px !important;
            min-height: 44px; /* iOS recommended touch target */
        }
        
        .message-icon {
            font-size: 1.1rem;
        }
        
        .reply-text,
        .reply-count-text {
            font-size: 0.9rem;
        }
    }

</style>