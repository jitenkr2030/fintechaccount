"""DRF serializers for the moderation app."""
from rest_framework import serializers

from .models import Report, ModerationAction


class ModerationActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationAction
        fields = ['id', 'report', 'admin', 'action', 'notes', 'created_at']
        read_only_fields = ['admin', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    actions = ModerationActionSerializer(many=True, read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'reporter', 'target_type', 'target_id', 'target_url',
                  'reason', 'description', 'status', 'assigned_to',
                  'resolution_notes', 'actions', 'created_at', 'updated_at']
        read_only_fields = ['reporter', 'status', 'assigned_to',
                            'resolution_notes', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)
