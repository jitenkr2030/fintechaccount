"""Views for the assessments app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView,
)

from .models import Assessment, Question, Choice, AssessmentAttempt, Answer
from .forms import AssessmentForm, QuestionForm, ChoiceFormSet, TakeAssessmentForm


# ---------------------------------------------------------------------------
# Assessment CRUD (instructors)
# ---------------------------------------------------------------------------
class AssessmentListView(LoginRequiredMixin, ListView):
    model = Assessment
    template_name = 'assessments/assessment_list.html'
    context_object_name = 'assessments'

    def get_queryset(self):
        user = self.request.user
        qs = Assessment.objects.select_related('course')
        if not user.is_admin_role:
            qs = qs.filter(created_by=user)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'assessments'
        return ctx


class AssessmentCreateView(LoginRequiredMixin, CreateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'assessments/assessment_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_instructor or request.user.is_admin_role):
            return HttpResponseForbidden('Instructors only.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        assessment = form.save(commit=False)
        assessment.created_by = self.request.user
        assessment.save()
        messages.success(self.request, f'Assessment "{assessment.title}" created.')
        return redirect('assessments:question_create', pk=assessment.pk)


class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'assessments/assessment_detail.html'
    context_object_name = 'assessment'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['questions'] = self.object.questions.all()
        ctx['attempts'] = self.object.attempts.filter(student=self.request.user)
        return ctx


class AssessmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assessment
    form_class = AssessmentForm
    template_name = 'assessments/assessment_form.html'

    def dispatch(self, request, *args, **kwargs):
        a = self.get_object()
        if a.created_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the author can edit.')
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Question creation
# ---------------------------------------------------------------------------
class QuestionCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'assessments/question_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        if self.assessment.created_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['assessment'] = self.assessment
        if 'form' not in kwargs:
            ctx['form'] = QuestionForm()
        if 'choice_formset' not in kwargs:
            ctx['choice_formset'] = ChoiceFormSet()
        return ctx

    def post(self, request, *args, **kwargs):
        form = QuestionForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST)
        if form.is_valid() and choice_formset.is_valid():
            question = form.save(commit=False)
            question.assessment = self.assessment
            question.save()
            choice_formset.instance = question
            choice_formset.save()
            messages.success(request, 'Question added.')
            return redirect('assessments:detail', pk=self.assessment.pk)
        return self.render_to_response(self.get_context_data(
            form=form, choice_formset=choice_formset,
        ))


# ---------------------------------------------------------------------------
# Take an assessment
# ---------------------------------------------------------------------------
class TakeAssessmentView(LoginRequiredMixin, View):
    """Render the assessment and grade the submission."""

    template_name = 'assessments/take.html'

    def dispatch(self, request, *args, **kwargs):
        self.assessment = get_object_or_404(
            Assessment, pk=kwargs['pk'], is_published=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Enforce max_attempts
        attempts_count = AssessmentAttempt.objects.filter(
            assessment=self.assessment, student=request.user,
        ).count()
        if attempts_count >= self.assessment.max_attempts:
            messages.error(request, 'You have used all your attempts.')
            return redirect('assessments:result', pk=self.assessment.pk)
        form = TakeAssessmentForm(assessment=self.assessment)
        return render(request, self.template_name, {
            'assessment': self.assessment,
            'form': form,
            'nav_active': 'assessments',
        })

    def post(self, request, *args, **kwargs):
        form = TakeAssessmentForm(request.POST, assessment=self.assessment)
        attempt = AssessmentAttempt.objects.create(
            assessment=self.assessment, student=request.user,
            status=AssessmentAttempt.STARTED,
        )
        total_marks = 0
        awarded = 0
        for question in self.assessment.questions.all():
            total_marks += question.marks
            answer = Answer.objects.create(
                attempt=attempt, question=question,
            )
            field = form.fields.get(f'q_{question.id}')
            if not field:
                continue
            value = form.cleaned_data.get(f'q_{question.id}')
            if question.question_type == Question.TEXT:
                answer.text_answer = value or ''
                answer.save()
            elif isinstance(value, list):
                for cid in value:
                    choice = Choice.objects.filter(id=cid, question=question).first()
                    if choice:
                        answer.selected_choices.add(choice)
            elif value:
                choice = Choice.objects.filter(id=value, question=question).first()
                if choice:
                    answer.selected_choices.add(choice)
            answer.grade()
            awarded += answer.marks_awarded

        # Compute score
        score_pct = int((awarded / total_marks * 100)) if total_marks else 0
        attempt.score_pct = score_pct
        attempt.is_passed = score_pct >= self.assessment.passing_score_pct
        attempt.status = AssessmentAttempt.GRADED if all(
            a.question.question_type != Question.TEXT for a in attempt.answers.all()
        ) else AssessmentAttempt.SUBMITTED
        attempt.submitted_at = timezone.now()
        attempt.save()
        messages.success(request, 'Assessment submitted.')
        return redirect('assessments:result', pk=self.assessment.pk)


class AssessmentResultView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'assessments/result.html'
    context_object_name = 'assessment'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['attempts'] = self.object.attempts.filter(
            student=self.request.user,
        ).order_by('-started_at')
        ctx['latest'] = ctx['attempts'].first()
        return ctx
