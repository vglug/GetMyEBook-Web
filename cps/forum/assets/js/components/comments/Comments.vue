<template>
    <div>
        <div class="comments-list">
            <Comment v-for="comment in comments" :comment="comment" :key="comment.id"
                :users="mentionableUsers"
                @delete="removeComment" @update="updateComment" @reply="handleReply"
            />
        </div>
        <CommentForm class="forum-chat-box" ref="commentForm" :threadId="id" :users="mentionableUsers" @submit="handleNewComment"/>
    </div>
</template>

<script>
import Comment from "./Comment.vue"
import CommentForm from "./CommentForm.vue"
import axios from "axios";

export default {
    components: {
        CommentForm, Comment
    },
    props: ['id'],
    data() {
        return {
            comments: []
        }
    },
    computed: {
        mentionableUsers() {
            const users = new Map();
            // Include current user for testing/self-mention
            if (window.Auth && window.Auth.id) {
                users.set(window.Auth.id, window.Auth);
            }
            this.comments.forEach(c => {
                if (c.owner && c.user_id) {
                    users.set(c.user_id, c.owner);
                }
            });
            return Array.from(users.values());
        }
    },
    mounted() {
        this.fetchComments();
    },
    methods: {
        fetchComments() {
             axios.get(`/forum/api/threads/${this.id}/comments`)
                .then(({data}) => this.comments = data.reverse())
                .catch(err => console.error("Error fetching comments:", err));

        },
        handleNewComment(comment) {
            this.comments.push(comment)
        },
        removeComment(deletedComment) {
            this.comments = this.comments.filter((comment) => comment.id !== deletedComment.id);
        },
        updateComment(updatedComment) {
            this.comments = this.comments.map(comment => {
                if(updatedComment.id === comment.id) {
                    comment = updatedComment;
                }

                return comment
            })
        },
        handleReply(payload) {
            // Check if this is an inline reply (has content)
            if (payload && payload.content && payload.originalComment) {
                this.submitInlineReply(payload);
                return;
            }

            // Legacy behavior (if payload is just comment object)
            const comment = payload; 
            const form = this.$refs.commentForm;
            if (form) {
                // Populate with username and focus
                form.content = `@${comment.owner.name} `;
                form.focusInput();
            }
        },
        submitInlineReply(payload) {
             // Optional: Prepend mention if desired, or just send content.
             // For now sending content as typed by user.
             // If mention is critical, we could add: `@${payload.originalComment.owner.name} ${payload.content}`
             // But usually inline reply implies context. 
             // Let's assume content is enough or user typed what they wanted.
             
             axios.post(`/forum/api/threads/${this.id}/comments`, { content: payload.content })
                .then(({data}) => {
                     this.handleNewComment(data);
                })
                .catch(error => console.error("Error posting inline reply:", error));
        }
    },
}
</script>
<style scoped>
    .forum-chat-box {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: #fff;
        padding: 12px;
        margin-left: 0.5%;
    }
    .comments-list{
        padding: 2rem;
        margin-bottom: 3.4rem !important;

    }
    /* 📱 Mobile Responsive */
    @media (max-width: 768px) {
        .comments-list {
            padding: 0.5rem;
        }
        .forum-chat-box{
            min-height: 50px;
        }
    }

</style>