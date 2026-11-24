"""Views for the courses app - catalog, detail, enrollment, progress, learn."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView,
)

from .models import (
    Category, Course, Module, Lesson, Enrollment,
    LessonProgress, CourseReview,
)
from .forms import CourseForm, ModuleForm, LessonForm, ReviewForm


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        qs = Course.objects.filter(status=Course.PUBLISHED)
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        is_free = self.request.GET.get('is_free')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(subtitle__icontains=q)
                | Q(description__icontains=q)
            )
        if category:
            qs = qs.filter(category__slug=category)
        if level:
            qs = qs.filter(level=level)
        if is_free == '1':
            qs = qs.filter(is_free=True)
        return qs.order_by('-is_featured', '-students_count', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'courses'
        ctx['categories'] = Category.objects.all()
        ctx['levels'] = Course.LEVELS
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_level'] = self.request.GET.get('level', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        # Allow instructor / admin to view drafts
        qs = Course.objects.all()
        if not (self.request.user.is_authenticated and
                (self.request.user.is_instructor or self.request.user.is_admin_role)):
            qs = qs.filter(status=Course.PUBLISHED)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'courses'
        ctx['modules'] = self.object.modules.prefetch_related('lessons').all()
        ctx['reviews'] = self.object.reviews.select_related('student').all()[:10]
        ctx['review_form'] = ReviewForm()
        if self.request.user.is_authenticated:
            ctx['enrollment'] = Enrollment.objects.filter(
                course=self.object, student=self.request.user,
            ).first()
        else:
            ctx['enrollment'] = None
        return ctx


class CategoryListView(ListView):
    model = Category
    template_name = 'courses/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'courses'
        return ctx


# ---------------------------------------------------------------------------
# Instructor CRUD on courses
# ---------------------------------------------------------------------------
class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_instructor or request.user.is_admin_role):
            return HttpResponseForbidden('Only instructors can create courses.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        course = form.save(commit=False)
        course.instructor = self.request.user
        course.save()
        messages.success(self.request, f'Course "{course.title}" created.')
        return redirect('courses:detail', slug=course.slug)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        if course.instructor_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the instructor can edit this course.')
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------
class EnrollView(LoginRequiredMixin, View):
    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug, status=Course.PUBLISHED)
        enrollment, created = Enrollment.objects.get_or_create(
            course=course, student=request.user,
            defaults={'status': Enrollment.ACTIVE},
        )
        if created:
            course.students_count += 1
            course.save(update_fields=['students_count'])
            messages.success(request, f'Enrolled in "{course.title}".')
            if course.is_free:
                return redirect('courses:learn', slug=course.slug)
            return redirect('payments:checkout',
                            content_type='course', object_id=course.id)
        messages.info(request, 'You are already enrolled.')
        return redirect('courses:learn', slug=course.slug)


class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user,
        ).select_related('course', 'course__instructor').order_by('-enrolled_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'courses'
        return ctx


class LearnView(LoginRequiredMixin, DetailView):
    """The student dashboard for an enrolled course."""

    model = Course
    template_name = 'courses/learn.html'
    context_object_name = 'course'

    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        enrollment = Enrollment.objects.filter(
            course=course, student=request.user, status=Enrollment.ACTIVE,
        ).first()
        if not enrollment and not request.user.is_admin_role:
            messages.error(request, 'You must be enrolled to access this course.')
            return redirect('courses:detail', slug=course.slug)
        self.enrollment = enrollment
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'courses'
        ctx['enrollment'] = self.enrollment
        ctx['modules'] = self.object.modules.prefetch_related('lessons').all()
        first_lesson = Lesson.objects.filter(module__course=self.object).order_by('order', 'id').first()
        ctx['first_lesson'] = first_lesson
        return ctx


class LessonView(LoginRequiredMixin, DetailView):
    """Show a single lesson with progress tracking."""

    model = Lesson
    template_name = 'courses/lesson.html'
    context_object_name = 'lesson'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Lesson, pk=self.kwargs['pk'],
            module__course__slug=self.kwargs['slug'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.object.module.course
        enrollment = Enrollment.objects.filter(
            course=course, student=self.request.user,
        ).first()
        ctx['course'] = course
        ctx['enrollment'] = enrollment
        ctx['modules'] = course.modules.prefetch_related('lessons').all()
        ctx['progress'], _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=self.object,
        ) if enrollment else (None, False)
        return ctx


class MarkLessonCompleteView(LoginRequiredMixin, View):
    def post(self, request, slug, pk):
        course = get_object_or_404(Course, slug=slug)
        lesson = get_object_or_404(Lesson, pk=pk, module__course=course)
        enrollment = get_object_or_404(
            Enrollment, course=course, student=request.user, status=Enrollment.ACTIVE,
        )
        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson,
        )
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'completed': True,
                                  'progress_pct': enrollment.progress_pct})
        messages.success(request, 'Lesson marked complete.')
        return redirect('courses:lesson', slug=slug, pk=pk)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = CourseReview
    form_class = ReviewForm

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        review, created = CourseReview.objects.get_or_create(
            course=course, student=self.request.user,
            defaults=form.cleaned_data,
        )
        if not created:
            review.rating = form.cleaned_data['rating']
            review.body = form.cleaned_data['body']
            review.save()
        messages.success(self.request, 'Thanks for your review!')
        return redirect('courses:detail', slug=course.slug)
