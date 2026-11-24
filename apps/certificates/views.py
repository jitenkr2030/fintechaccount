"""Views for the certificates app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View, TemplateView

from .models import Certificate


class MyCertificatesView(LoginRequiredMixin, ListView):
    """List of the current user's certificates."""

    model = Certificate
    template_name = 'certificates/my_certificates.html'
    context_object_name = 'certificates'

    def get_queryset(self):
        return Certificate.objects.filter(
            user=self.request.user, status=Certificate.ISSUED,
        ).select_related('course', 'user')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'certificates'
        return ctx


class CertificateDetailView(DetailView):
    """Public certificate view (verified by certificate_id + verification_code).

    Visible to anyone who knows the verification code (for employer checks).
    """

    model = Certificate
    template_name = 'certificates/certificate_detail.html'
    context_object_name = 'certificate'

    def get_object(self, queryset=None):
        cert_id = self.kwargs.get('certificate_id')
        code = self.request.GET.get('code') or self.kwargs.get('code')
        cert = get_object_or_404(
            Certificate, certificate_id=cert_id, status=Certificate.ISSUED,
        )
        # Public preview allowed; verification code shown only on the holder's view
        return cert


class VerifyCertificateView(View):
    """Public verification endpoint: check a certificate_id + code."""

    template_name = 'certificates/verify.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'nav_active': 'verify'})

    def post(self, request, *args, **kwargs):
        cert_id = request.POST.get('certificate_id', '').strip()
        code = request.POST.get('verification_code', '').strip()
        certificate = None
        valid = False
        if cert_id and code:
            try:
                cert = Certificate.objects.get(
                    certificate_id=cert_id, status=Certificate.ISSUED,
                )
                if str(cert.verification_code).lower() == code.lower():
                    certificate = cert
                    valid = True
            except Certificate.DoesNotExist:
                pass
        return render(request, self.template_name, {
            'certificate': certificate,
            'valid': valid,
            'nav_active': 'verify',
            'submitted': True,
        })


class CertificateDownloadView(LoginRequiredMixin, View):
    """Download a real PDF copy of the user's own certificate.

    Uses WeasyPrint to render a styled A4-landscape PDF. If the PDF has
    already been generated it is served from storage; otherwise it is
    generated on demand and cached on the Certificate.pdf field for reuse.
    Falls back to the printable HTML page if WeasyPrint is unavailable.
    """

    def get(self, request, certificate_id):
        cert = get_object_or_404(
            Certificate, certificate_id=certificate_id, user=request.user,
            status=Certificate.ISSUED,
        )
        # If a PDF already exists, serve it
        if cert.pdf:
            try:
                from django.http import FileResponse
                return FileResponse(cert.pdf.open('rb'),
                                    content_type='application/pdf',
                                    filename=f'certificate-{cert.certificate_id}.pdf')
            except Exception:
                pass  # fall through to regeneration

        # Generate the PDF with WeasyPrint
        from .pdf import render_certificate_pdf, WEASYPRINT_AVAILABLE
        if not WEASYPRINT_AVAILABLE:
            # Fallback: printable HTML page
            return render(request, 'certificates/printable.html', {
                'certificate': cert,
            })

        pdf_bytes = render_certificate_pdf(cert)
        if not pdf_bytes:
            return render(request, 'certificates/printable.html', {
                'certificate': cert,
            })

        # Cache the generated PDF on the model
        import io
        from django.core.files.base import ContentFile
        cert.pdf.save(
            f'certificate-{cert.certificate_id}.pdf',
            ContentFile(pdf_bytes),
            save=True,
        )

        from django.http import HttpResponse
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="certificate-{cert.certificate_id}.pdf"'
        )
        return response

