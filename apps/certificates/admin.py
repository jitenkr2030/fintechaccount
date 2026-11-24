"""Admin for the certificates app."""
from django.contrib import admin

from .models import Certificate, CertificateTemplate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'user', 'course', 'status',
                    'final_score_pct', 'grade', 'issued_at')
    list_filter = ('status', 'issued_at')
    search_fields = ('certificate_id', 'user__email', 'course__title')
    readonly_fields = ('certificate_id', 'verification_code', 'issued_at',
                       'is_platform_issued', 'disclaimer', 'created_at')
    actions = ['revoke_certificates']

    def revoke_certificates(self, request, queryset):
        updated = queryset.update(status=Certificate.REVOKED)
        self.message_user(request, f'{updated} certificate(s) revoked.')
    revoke_certificates.short_description = 'Revoke selected certificates'


admin.site.register(CertificateTemplate)
