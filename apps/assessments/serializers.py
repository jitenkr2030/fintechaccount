"""DRF serializers for the assessments app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Assessment, Question, Choice, AssessmentAttempt, Answer

User = get_user_model()


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'body', 'is_correct', 'order']
        # Hide is_correct in student-facing list - handled per-view


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'assessment', 'body', 'question_type', 'marks',
                  'explanation', 'order', 'choices']
        read_only_fields = ['explanation']  # students should not see explanation upfront


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    attempt_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'description', 'assessment_type',
                  'course', 'module', 'duration_minutes', 'passing_score_pct',
                  'max_attempts', 'is_published', 'shuffle_questions',
                  'show_answers_after', 'questions', 'attempt_count',
                  'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_attempt_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return obj.attempts.filter(student=request.user).count()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    selected_choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'attempt', 'question', 'selected_choices',
                  'text_answer', 'is_correct', 'marks_awarded']
        read_only_fields = ['is_correct', 'marks_awarded']


class AssessmentAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentAttempt
        fields = ['id', 'assessment', 'student', 'status',
                  'started_at', 'submitted_at', 'score_pct', 'is_passed']
        read_only_fields = ['student', 'started_at', 'submitted_at',
                            'score_pct', 'is_passed']
