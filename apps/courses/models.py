"""Courses app - LMS catalog, lessons, enrollment, progress (Pillar B spec).

Course categories from spec section 2 (Pillar B):
  Accounting, Taxation, Software, Finance, FinTech, Technology,
  Capital Markets, Professional Skills.

Learning features implemented:
  - Free and paid courses
  - Recorded and live classes
  - Instructor profiles (see instructors app)
  - Student dashboard
  - Assignments and examinations (see assessments app)
  - Course completion certificates (see certificates app)
  - Learning progress tracking
  - Discussion forums (uses communities under the hood)
  - Corporate training / institution partnerships (see instructors app)
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Course Category
# ---------------------------------------------------------------------------
class Category(models.Model):
    """A top-level course category.

    Pre-seeded per spec: Accounting, Taxation, Software, Finance, FinTech,
    Technology, Capital Markets, Professional Skills.
    """

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True,
                             help_text='Bootstrap Icons name, e.g. calculator')

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------
class Course(models.Model):
    """A course in the LMS catalog."""

    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    STATUSES = [(DRAFT, 'Draft'), (PUBLISHED, 'Published'), (ARCHIVED, 'Archived')]

    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    LEVELS = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]

    RECORDED = 'recorded'
    LIVE = 'live'
    HYBRID = 'hybrid'
    DELIVERY = [
        (RECORDED, 'Recorded (self-paced)'),
        (LIVE, 'Live classes'),
        (HYBRID, 'Hybrid (recorded + live)'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,
                                  related_name='courses')
    level = models.CharField(max_length=20, choices=LEVELS, default=BEGINNER)
    delivery = models.CharField(max_length=20, choices=DELIVERY, default=RECORDED)
    status = models.CharField(max_length=20, choices=STATUSES, default=DRAFT)

    # Instructor ( FK -> User who must have role 'instructor')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='courses_taught',
    )

    # Media
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    promo_video_url = models.URLField(blank=True)

    # Pricing (Revenue model: paid courses ₹499-4,999)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Scheduling (for live/hybrid)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    duration_hours = models.PositiveIntegerField(default=0,
                                                  help_text='Approximate total hours of content')

    # Stats
    students_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)

    # Meta
    is_featured = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=True,
                                       help_text='Issue a course-completion certificate on completion')
    is_corporate = models.BooleanField(default=False,
                                        help_text='Available as corporate training')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:220] or 'course'
            candidate = base
            i = 2
            while Course.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{i}'
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        """The price actually charged (discount price if set, else price)."""
        if self.is_free:
            return 0
        return self.discount_price or self.price


# ---------------------------------------------------------------------------
# Modules & Lessons
# ---------------------------------------------------------------------------
class Module(models.Model):
    """A module (chapter) inside a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Lesson(models.Model):
    """A lesson (unit) inside a module.

    ``content_type`` describes whether the lesson is a video, reading
    material, live session or assignment. Video hosting is external
    (per architecture spec) - we store a URL rather than a file.
    """

    VIDEO = 'video'
    READING = 'reading'
    LIVE = 'live'
    ASSIGNMENT = 'assignment'
    QUIZ = 'quiz'
    TYPES = [
        (VIDEO, 'Video'),
        (READING, 'Reading'),
        (LIVE, 'Live session'),
        (ASSIGNMENT, 'Assignment'),
        (QUIZ, 'Quiz'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=TYPES, default=VIDEO)
    body = models.TextField(blank=True, help_text='For reading lessons: markdown/text')
    video_url = models.URLField(blank=True,
                                 help_text='External hosted video (YouTube/Vimeo/etc.)')
    duration_minutes = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False,
                                     help_text='Available to non-enrolled users as a preview')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.module.title} - {self.title}'


# ---------------------------------------------------------------------------
# Enrollment & Progress
# ---------------------------------------------------------------------------
class Enrollment(models.Model):
    """A student's enrollment in a course (free or paid)."""

    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    STATUSES = [
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (REFUNDED, 'Refunded'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUSES, default=ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_pct = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('course', 'student')]

    def __str__(self):
        return f'{self.student} -> {self.course}'

    def update_progress(self):
        """Recompute progress from LessonProgress records."""
        lessons = self.course.modules.values_list('lessons', flat=True)
        from django.db.models import Count
        total = Lesson.objects.filter(module__course=self.course).count()
        completed = LessonProgress.objects.filter(
            enrollment=self, is_completed=True,
        ).count()
        if total:
            self.progress_pct = int((completed / total) * 100)
            self.save(update_fields=['progress_pct'])
        if self.progress_pct == 100 and self.status != self.COMPLETED:
            from django.utils import timezone
            self.status = self.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'completed_at'])


class LessonProgress(models.Model):
    """Track per-lesson progress for an enrollment."""

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE,
                                    related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,
                                related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    position_seconds = models.PositiveIntegerField(default=0,
                                                    help_text='Last video playhead position')
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('enrollment', 'lesson')]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_completed:
            self.enrollment.update_progress()


class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='course_reviews')
    rating = models.PositiveIntegerField(default=5,
                                          help_text='1 to 5 stars')
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('course', 'student')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} rated {self.course} {self.rating}/5'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        # Update aggregate rating
        from django.db.models import Avg, Count
        agg = CourseReview.objects.filter(course=self.course).aggregate(
            avg=Avg('rating'), count=Count('id'),
        )
        self.course.rating = round(agg['avg'] or 0, 2)
        self.course.reviews_count = agg['count']
        self.course.save(update_fields=['rating', 'reviews_count'])
