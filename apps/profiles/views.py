"""Views for the profiles app - extended professional profile management."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView, UpdateView, TemplateView, CreateView, DeleteView, ListView,
)
from django.contrib.auth import get_user_model

from .models import (
    Profile, Education, Experience, Certification, ProfileSkill, PortfolioItem,
)
from .forms import (
    ProfileForm, EducationForm, ExperienceForm, CertificationForm,
    PortfolioItemForm, ProfileSkillForm,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Public profile view
# ---------------------------------------------------------------------------
class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'
    slug_url_kwarg = 'slug'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'profile_view'
        ctx['is_owner'] = (
            self.request.user.is_authenticated
            and self.object.user_id == self.request.user.id
        )
        return ctx


# ---------------------------------------------------------------------------
# Edit own profile + sections
# ---------------------------------------------------------------------------
class MyProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_edit.html'
    success_url = reverse_lazy('profiles:my_edit')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, 'Professional profile updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'profile'
        ctx['completion'] = self.request.user.profile.completion_pct
        return ctx


class ProfileSectionCreateView(LoginRequiredMixin, CreateView):
    """Generic create view for the profile section models.

    The ``section`` kwarg selects which form/model to use.
    """

    template_name = 'profiles/section_form.html'
    section_map = {
        'education': (EducationForm, Education),
        'experience': (ExperienceForm, Experience),
        'certification': (CertificationForm, Certification),
        'portfolio': (PortfolioItemForm, PortfolioItem),
        'skill': (ProfileSkillForm, ProfileSkill),
    }
    section_labels = {
        'education': 'Education',
        'experience': 'Work Experience',
        'certification': 'Certification',
        'portfolio': 'Portfolio Item',
        'skill': 'Skill',
    }

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('section') not in self.section_map:
            raise Http404('Unknown profile section')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.section_map[self.kwargs['section']][0]

    def get_model(self):
        return self.section_map[self.kwargs['section']][1]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.profile = self.request.user.profile
        obj.save()
        messages.success(self.request, f'{self.section_labels[self.kwargs["section"]]} added.')
        return redirect('profiles:my_edit')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        section = self.kwargs['section']
        ctx['section'] = section
        ctx['section_label'] = self.section_labels[section]
        ctx['nav_active'] = 'profile'
        return ctx


class ProfileSectionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a section item that belongs to the current user."""

    template_name = 'profiles/section_confirm_delete.html'
    section_models = {
        'education': Education,
        'experience': Experience,
        'certification': Certification,
        'portfolio': PortfolioItem,
        'skill': ProfileSkill,
    }

    def get_model(self):
        return self.section_models[self.kwargs['section']]

    def get_queryset(self):
        model = self.get_model()
        return model.objects.filter(profile=self.request.user.profile)

    def get_success_url(self):
        return reverse_lazy('profiles:my_edit')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['section'] = self.kwargs['section']
        return ctx


# ---------------------------------------------------------------------------
# Resume download / view
# ---------------------------------------------------------------------------
class ResumeView(LoginRequiredMixin, DetailView):
    """Simple HTML 'printable resume' view of the current user."""

    template_name = 'profiles/resume.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile
