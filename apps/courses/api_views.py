"""DRF API views for the courses app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .models import (
    Category, Course, Module, Lesson, Enrollment,
    LessonProgress, CourseReview,
)
from .serializers import (
    CategorySerializer, CourseSerializer, ModuleSerializer, LessonSerializer,
    EnrollmentSerializer, LessonProgressSerializer, CourseReviewSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['category', 'level', 'delivery', 'is_free', 'is_featured']
    search_fields = ['title', 'subtitle', 'description']

    def get_queryset(self):
        qs = Course.objects.filter(status=Course.PUBLISHED)
        if self.request.user.is_authenticated and (
            self.request.user.is_instructor or self.request.user.is_admin_role
        ):
            if self.request.query_params.get('include_drafts') == '1':
                qs = Course.objects.all()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(subtitle__icontains=q)
                | Q(description__icontains=q)
            )
        return qs.order_by('-is_featured', '-students_count')

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(
            course=course, student=request.user,
            defaults={'status': Enrollment.ACTIVE},
        )
        if created:
            course.students_count += 1
            course.save(update_fields=['students_count'])
        return Response(EnrollmentSerializer(enrollment).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['course']


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['module', 'content_type']


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']

    def get_queryset(self):
        qs = Enrollment.objects.select_related('course', 'student')
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(student=self.request.user)

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        enrollment, created = Enrollment.objects.get_or_create(
            course=course, student=self.request.user,
            defaults={'status': Enrollment.ACTIVE},
        )
        if created:
            course.students_count += 1
            course.save(update_fields=['students_count'])
        return enrollment


class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_admin_role:
            qs = qs.filter(enrollment__student=self.request.user)
        return qs


class CourseReviewViewSet(viewsets.ModelViewSet):
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['course']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
