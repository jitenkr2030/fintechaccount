"""Views for the networking app - news feed, posts, comments, connections."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView,
)

from apps.accounts.models import User
from .models import Connection, Post, Comment, Like
from .forms import PostForm, CommentForm


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------
class FeedView(LoginRequiredMixin, ListView):
    """Personalised feed: posts by the user + their connections, plus trending."""

    template_name = 'networking/feed.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        # IDs of users this person follows
        following_ids = list(Connection.objects.filter(
            from_user=user, status=Connection.ACCEPTED,
        ).values_list('to_user_id', flat=True))
        following_ids.append(user.id)
        qs = Post.objects.filter(
            Q(author_id__in=following_ids) | Q(is_pinned=True)
        ).select_related('author', 'author__profile').distinct()
        return qs.order_by('-is_pinned', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'feed'
        ctx['post_form'] = PostForm()
        # Suggested members (people not yet connected)
        connected_ids = set(Connection.objects.filter(
            from_user=self.request.user,
        ).values_list('to_user_id', flat=True))
        connected_ids.add(self.request.user.id)
        ctx['suggestions'] = (
            User.objects.filter(is_active=True)
            .exclude(id__in=connected_ids)
            .exclude(is_superuser=True)[:5]
        )
        # Trending posts (most liked in last 7 days)
        from datetime import timedelta
        from django.utils import timezone
        week_ago = timezone.now() - timedelta(days=7)
        ctx['trending'] = Post.objects.filter(
            created_at__gte=week_ago,
        ).order_by('-likes_count')[:5]
        return ctx


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'networking/post_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        form.save_m2m()
        messages.success(self.request, 'Post published.')
        return redirect('networking:feed')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'networking/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['comments'] = self.object.comments.select_related('author').all()
        ctx['comment_form'] = CommentForm()
        ctx['user_liked'] = self.object.likes.filter(user=self.request.user).exists()
        return ctx


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'networking/post_form.html'

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Post updated.')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'networking/post_confirm_delete.html'
    success_url = reverse_lazy('networking:feed')

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        comment.save()
        messages.success(self.request, 'Comment added.')
        return redirect('networking:post_detail', pk=post.pk)


# ---------------------------------------------------------------------------
# Likes
# ---------------------------------------------------------------------------
class LikeToggleView(LoginRequiredMixin, View):
    """Toggle like on a post."""

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            post.increment_likes(-1)
            liked = False
        else:
            Like.objects.create(user=request.user, post=post)
            post.increment_likes(1)
            liked = True
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'liked': liked, 'count': post.likes_count})
        return redirect('networking:post_detail', pk=pk)


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------
class ConnectionToggleView(LoginRequiredMixin, View):
    """Follow / unfollow a user, or send / withdraw a connect request."""

    def post(self, request, user_id):
        target = get_object_or_404(User, pk=user_id, is_active=True)
        if target == request.user:
            return HttpResponseForbidden()
        kind = request.POST.get('kind', Connection.FOLLOW)
        existing = Connection.objects.filter(
            from_user=request.user, to_user=target, kind=kind,
        ).first()
        if existing:
            existing.delete()
            messages.info(request, f'Unfollowed {target.get_full_name()}.')
        else:
            Connection.objects.create(
                from_user=request.user, to_user=target, kind=kind,
                status=Connection.ACCEPTED if kind == Connection.FOLLOW else Connection.PENDING,
            )
            if kind == Connection.FOLLOW:
                messages.success(request, f'Following {target.get_full_name()}.')
            else:
                messages.success(request, f'Connection request sent to {target.get_full_name()}.')
        return redirect('profiles:detail', slug=target.profile.slug)


class ConnectionsView(LoginRequiredMixin, TemplateView):
    """Show the user's followers, following and pending connection requests."""

    template_name = 'networking/connections.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['following'] = Connection.objects.filter(
            from_user=user, kind=Connection.FOLLOW, status=Connection.ACCEPTED,
        ).select_related('to_user')
        ctx['followers'] = Connection.objects.filter(
            to_user=user, kind=Connection.FOLLOW, status=Connection.ACCEPTED,
        ).select_related('from_user')
        ctx['pending'] = Connection.objects.filter(
            to_user=user, kind=Connection.CONNECT, status=Connection.PENDING,
        ).select_related('from_user')
        ctx['nav_active'] = 'connections'
        return ctx


class ConnectionActionView(LoginRequiredMixin, View):
    """Accept or decline an incoming connection request."""

    def post(self, request, pk, action):
        conn = get_object_or_404(
            Connection, pk=pk, to_user=request.user, kind=Connection.CONNECT,
            status=Connection.PENDING,
        )
        if action == 'accept':
            conn.accept()
            messages.success(request, f'Connected with {conn.from_user.get_full_name()}.')
        elif action == 'decline':
            conn.status = Connection.DECLINED
            conn.save(update_fields=['status'])
            messages.info(request, 'Connection request declined.')
        return redirect('networking:connections')
