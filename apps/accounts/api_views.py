"""DRF API views for accounts."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Role
from .serializers import UserSerializer, UserCreateSerializer, RoleSerializer

User = get_user_model()


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).exclude(is_superuser=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('create',):
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        role = self.request.query_params.get('role')
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(headline__icontains=q) | Q(city__icontains=q)
            )
        if role:
            qs = qs.filter(roles__name=role)
        return qs.distinct()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Return the current authenticated user's profile."""
        return Response(UserSerializer(request.user, context={'request': request}).data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_role(self, request):
        name = request.data.get('role')
        if not name:
            return Response({'detail': 'role is required.'}, status=status.HTTP_400_BAD_REQUEST)
        added = request.user.add_role(name)
        return Response({'added': added, 'roles': [r.name for r in request.user.roles.all()]})
