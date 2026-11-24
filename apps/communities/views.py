"""Views for the communities app."""
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView,
)

from .models import Community, CommunityMembership, CommunityTopic, CommunityReply
from .forms import CommunityForm, TopicForm, ReplyForm


class CommunityListView(ListView):
    model = Community
    template_name = 'communities/community_list.html'
    context_object_name = 'communities'
    paginate_by = 24

    def get_queryset(self):
        qs = Community.objects.annotate(topic_count=Count('topics'))
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
        if cat:
            qs = qs.filter(category__icontains=cat)
        return qs.distinct().order_by('-is_official', '-members_count')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'communities'
        ctx['categories'] = [
            'Accounting', 'Taxation', 'FinTech', 'Banking',
            'Investment', 'Software', 'Students',
        ]
        return ctx


class CommunityDetailView(DetailView):
    model = Community
    template_name = 'communities/community_detail.html'
    context_object_name = 'community'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topics'] = self.object.topics.order_by('-is_pinned', '-created_at')[:20]
        ctx['nav_active'] = 'communities'
        if self.request.user.is_authenticated:
            ctx['is_member'] = CommunityMembership.objects.filter(
                community=self.object, user=self.request.user, status=CommunityMembership.ACTIVE,
            ).exists()
            ctx['has_pending'] = CommunityMembership.objects.filter(
                community=self.object, user=self.request.user, status=CommunityMembership.PENDING,
            ).exists()
        else:
            ctx['is_member'] = False
            ctx['has_pending'] = False
        return ctx


class CommunityCreateView(LoginRequiredMixin, CreateView):
    model = Community
    form_class = CommunityForm
    template_name = 'communities/community_form.html'

    def form_valid(self, form):
        community = form.save(commit=False)
        community.owner = self.request.user
        community.save()
        CommunityMembership.objects.create(
            community=community, user=self.request.user,
            role=CommunityMembership.OWNER, status=CommunityMembership.ACTIVE,
        )
        community.members_count = 1
        community.save(update_fields=['members_count'])
        messages.success(self.request, f'Community "{community.name}" created.')
        return redirect('communities:detail', slug=community.slug)


class CommunityUpdateView(LoginRequiredMixin, UpdateView):
    model = Community
    form_class = CommunityForm
    template_name = 'communities/community_form.html'

    def dispatch(self, request, *args, **kwargs):
        community = self.get_object()
        if community.owner_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the owner can edit this community.')
        return super().dispatch(request, *args, **kwargs)


class JoinCommunityView(LoginRequiredMixin, View):
    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)
        membership, created = CommunityMembership.objects.get_or_create(
            community=community, user=request.user,
            defaults={
                'status': CommunityMembership.PENDING if community.visibility != Community.PUBLIC
                else CommunityMembership.ACTIVE,
            },
        )
        if not created:
            if membership.status == CommunityMembership.BANNED:
                messages.error(request, 'You are banned from this community.')
            elif membership.status == CommunityMembership.PENDING:
                messages.info(request, 'Your join request is pending approval.')
            else:
                messages.info(request, 'You are already a member.')
        else:
            if membership.status == CommunityMembership.ACTIVE:
                community.members_count += 1
                community.save(update_fields=['members_count'])
                messages.success(request, f'Joined {community.name}.')
            else:
                messages.success(request, f'Join request sent for {community.name}.')
        return redirect('communities:detail', slug=slug)


class LeaveCommunityView(LoginRequiredMixin, View):
    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)
        CommunityMembership.objects.filter(
            community=community, user=request.user,
        ).delete()
        community.members_count = max(0, community.members_count - 1)
        community.save(update_fields=['members_count'])
        messages.info(request, f'Left {community.name}.')
        return redirect('communities:detail', slug=slug)


# ---------------------------------------------------------------------------
# Topics / threads
# ---------------------------------------------------------------------------
class TopicCreateView(LoginRequiredMixin, CreateView):
    model = CommunityTopic
    form_class = TopicForm
    template_name = 'communities/topic_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.community = get_object_or_404(Community, slug=kwargs['slug'])
        is_member = CommunityMembership.objects.filter(
            community=self.community, user=request.user, status=CommunityMembership.ACTIVE,
        ).exists()
        if not is_member and not request.user.is_admin_role:
            return HttpResponseForbidden('Join this community to start a topic.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        topic = form.save(commit=False)
        topic.community = self.community
        topic.author = self.request.user
        topic.save()
        self.community.posts_count += 1
        self.community.save(update_fields=['posts_count'])
        messages.success(self.request, 'Topic created.')
        return redirect('communities:topic_detail', slug=self.community.slug, pk=topic.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['community'] = self.community
        return ctx


class TopicDetailView(DetailView):
    model = CommunityTopic
    template_name = 'communities/topic_detail.html'
    context_object_name = 'topic'

    def get_object(self, queryset=None):
        return get_object_or_404(
            CommunityTopic, pk=self.kwargs['pk'],
            community__slug=self.kwargs['slug'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['community'] = self.object.community
        ctx['replies'] = self.object.replies.select_related('author').all()
        ctx['reply_form'] = ReplyForm()
        return ctx

    def get(self, request, *args, **kwargs):
        # increment views
        topic = self.get_object()
        topic.views_count += 1
        topic.save(update_fields=['views_count'])
        return super().get(request, *args, **kwargs)


class ReplyCreateView(LoginRequiredMixin, CreateView):
    model = CommunityReply
    form_class = ReplyForm

    def form_valid(self, form):
        topic = get_object_or_404(
            CommunityTopic, pk=self.kwargs['pk'],
            community__slug=self.kwargs['slug'],
        )
        reply = form.save(commit=False)
        reply.topic = topic
        reply.author = self.request.user
        reply.save()
        topic.replies_count += 1
        topic.save(update_fields=['replies_count'])
        messages.success(self.request, 'Reply posted.')
        return redirect('communities:topic_detail', slug=topic.community.slug, pk=topic.pk)
