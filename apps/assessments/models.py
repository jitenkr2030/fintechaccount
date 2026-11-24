"""Assessments app - quizzes, exams, questions, attempts (Pillar B spec).

Implements:
  - Assignments and examinations
  - Skill assessment (Phase 5 builds on this)

Linked to a course (Assessment) or standalone (skill assessment).
"""
from django.conf import settings
from django.db import models


class Assessment(models.Model):
    """A quiz/exam/assignment tied to a course, or a standalone skill test."""

    QUIZ = 'quiz'
    EXAM = 'exam'
    ASSIGNMENT = 'assignment'
    SKILL_TEST = 'skill_test'
    TYPES = [
        (QUIZ, 'Quiz'),
        (EXAM, 'Exam'),
        (ASSIGNMENT, 'Assignment'),
        (SKILL_TEST, 'Skill Test'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=TYPES, default=QUIZ)

    # Optional link to a course/module
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, null=True, blank=True,
        related_name='assessments',
    )
    module = models.ForeignKey(
        'courses.Module', on_delete=models.CASCADE, null=True, blank=True,
        related_name='assessments',
    )

    # Config
    duration_minutes = models.PositiveIntegerField(default=30)
    passing_score_pct = models.PositiveIntegerField(default=60)
    max_attempts = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)
    shuffle_questions = models.BooleanField(default=False)
    show_answers_after = models.BooleanField(default=True,
                                              help_text='Reveal correct answers after submission')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='created_assessments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    """A multiple-choice question in an assessment."""

    SINGLE = 'single'
    MULTIPLE = 'multiple'
    TEXT = 'text'
    TYPES = [
        (SINGLE, 'Single correct answer'),
        (MULTIPLE, 'Multiple correct answers'),
        (TEXT, 'Free text answer'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    body = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPES, default=SINGLE)
    marks = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.assessment}: {self.body[:60]}'


class Choice(models.Model):
    """A possible answer to a question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    body = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.body


class AssessmentAttempt(models.Model):
    """A student's attempt at an assessment."""

    STARTED = 'started'
    SUBMITTED = 'submitted'
    GRADED = 'graded'
    EXPIRED = 'expired'
    STATUSES = [
        (STARTED, 'Started'),
        (SUBMITTED, 'Submitted'),
        (GRADED, 'Graded'),
        (EXPIRED, 'Expired'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='assessment_attempts')
    status = models.CharField(max_length=20, choices=STATUSES, default=STARTED)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score_pct = models.PositiveIntegerField(default=0)
    is_passed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.student} - {self.assessment} ({self.status})'


class Answer(models.Model):
    """A student's answer to one question in an attempt."""

    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='answers')
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('attempt', 'question')]

    def grade(self):
        """Auto-grade: correct iff the chosen choices match the question's
        correct choices exactly (single/multiple). Text answers are manually
        graded via admin."""
        if self.question.question_type == Question.TEXT:
            return  # needs manual grading
        correct_ids = set(self.question.choices.filter(is_correct=True).values_list('id', flat=True))
        chosen_ids = set(self.selected_choices.values_list('id', flat=True))
        self.is_correct = correct_ids == chosen_ids
        self.marks_awarded = self.question.marks if self.is_correct else 0
        self.save(update_fields=['is_correct', 'marks_awarded'])
