"""DRF API views for the assessments app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Assessment, Question, Choice, AssessmentAttempt, Answer
from .serializers import (
    AssessmentSerializer, QuestionSerializer, ChoiceSerializer,
    AssessmentAttemptSerializer, AnswerSerializer,
)


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['assessment_type', 'course', 'is_published']

    def get_queryset(self):
        if self.request.user.is_authenticated and (
            self.request.user.is_instructor or self.request.user.is_admin_role
        ):
            return super().get_queryset()
        return super().get_queryset().filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['assessment']


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['question', 'is_correct']


class AssessmentAttemptViewSet(viewsets.ModelViewSet):
    queryset = AssessmentAttempt.objects.all()
    serializer_class = AssessmentAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['assessment', 'student', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        """Submit answers for an attempt.

        Expected payload: {
            "answers": [
                {"question": <id>, "choice_ids": [<id>, ...], "text": "..."}
            ]
        }
        """
        attempt = self.get_object()
        if attempt.student_id != request.user.id:
            return Response({'detail': 'Not your attempt.'},
                            status=status.HTTP_403_FORBIDDEN)
        if attempt.status != AssessmentAttempt.STARTED:
            return Response({'detail': 'Already submitted.'},
                            status=status.HTTP_400_BAD_REQUEST)
        total = 0
        awarded = 0
        for ans_data in request.data.get('answers', []):
            question = Question.objects.filter(id=ans_data.get('question')).first()
            if not question or question.assessment_id != attempt.assessment_id:
                continue
            total += question.marks
            answer, _ = Answer.objects.get_or_create(attempt=attempt, question=question)
            answer.text_answer = ans_data.get('text', '')
            answer.save()
            choice_ids = ans_data.get('choice_ids', [])
            answer.selected_choices.set(choice_ids)
            answer.grade()
            awarded += answer.marks_awarded
        attempt.score_pct = int((awarded / total * 100)) if total else 0
        attempt.is_passed = attempt.score_pct >= attempt.assessment.passing_score_pct
        attempt.status = AssessmentAttempt.GRADED
        attempt.submitted_at = timezone.now()
        attempt.save()
        return Response(AssessmentAttemptSerializer(attempt).data)


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['attempt', 'question']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(attempt__student=self.request.user)
