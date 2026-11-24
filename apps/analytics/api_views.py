from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recommendation, UserActivity
from .serializers import RecommendationSerializer, UserActivitySerializer
from .recommenders import recommend_courses, recommend_jobs

class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['source', 'is_dismissed']

    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refresh(self, request):
        recommend_courses(request.user)
        recommend_jobs(request.user)
        return Response({'refreshed': True})

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
