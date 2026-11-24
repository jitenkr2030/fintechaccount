"""DRF API views for the certificates app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Certificate, CertificateTemplate
from .serializers import (
    CertificateSerializer, CertificateTemplateSerializer,
)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.select_related('user', 'course').all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'certificate_id'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify(self, request):
        """Public verification endpoint."""
        cert_id = request.data.get('certificate_id')
        code = request.data.get('verification_code')
        try:
            cert = Certificate.objects.get(
                certificate_id=cert_id, status=Certificate.ISSUED,
            )
            valid = str(cert.verification_code).lower() == str(code).lower()
        except Certificate.DoesNotExist:
            valid = False
            cert = None
        return Response({
            'valid': valid,
            'certificate': CertificateSerializer(cert).data if cert and valid else None,
        })


class CertificateTemplateViewSet(viewsets.ModelViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
