"""WeasyPrint-powered PDF certificate generator.

Generates a real PDF certificate (A4 landscape) from the Certificate model.
Falls back gracefully if WeasyPrint is not installed or font deps are missing.
"""
import io
import logging

from django.conf import settings
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:  # pragma: no cover
    WEASYPRINT_AVAILABLE = False


CERTIFICATE_CSS = """
@page {
  size: A4 landscape;
  margin: 0;
}
* { box-sizing: border-box; }
body {
  font-family: 'Inter','DejaVu Sans','Segoe UI',sans-serif;
  color: #1f2937; margin: 0; padding: 0;
}
.certificate {
  width: 100%; min-height: 100vh;
  background: linear-gradient(135deg,#ffffff,#fafbfd);
  border: 14px double #0a2540;
  padding: 3.5rem 4rem;
  text-align: center; position: relative;
}
.certificate .corner {
  position: absolute; width: 90px; height: 90px;
  background: linear-gradient(135deg,#c8a45c,#b08d3e); border-radius: 10px;
}
.certificate .corner.tl { top: -14px; left: -14px; clip-path: polygon(0 0,100% 0,0 100%); }
.certificate .corner.br { bottom: -14px; right: -14px; clip-path: polygon(100% 0,100% 100%,0 100%); }
.certificate .brand {
  display: flex; align-items: center; justify-content: center; gap: .6rem;
  margin-bottom: .5rem;
}
.certificate .brand .mark {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg,#0a2540,#1a3a6b); color: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 800;
}
.certificate .brand .name { font-size: 1.1rem; font-weight: 800; color: #0a2540; }
.certificate .eyebrow {
  font-size: .8rem; letter-spacing: .25em; text-transform: uppercase;
  color: #b08d3e; font-weight: 700; margin: 1.5rem 0 .5rem;
}
.certificate h1 {
  font-size: 2.6rem; color: #0a2540; margin: .5rem 0;
  font-weight: 800; letter-spacing: -.01em;
}
.certificate .awarded { font-size: 1rem; color: #6b7280; margin: 1rem 0 .3rem; }
.certificate .name {
  font-size: 2rem; color: #0a2540; font-weight: 700; margin: .5rem 0 1rem;
  border-bottom: 2px solid #c8a45c; display: inline-block; padding-bottom: .3rem;
}
.certificate .course-label { font-size: 1rem; color: #6b7280; margin: 1rem 0 .3rem; }
.certificate .course-name { font-size: 1.5rem; color: #1a3a6b; font-weight: 600; }
.certificate .seal {
  width: 90px; height: 90px; border-radius: 50%; margin: 1.5rem auto;
  background: radial-gradient(circle,#c8a45c,#b08d3e);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 2.2rem; box-shadow: 0 4px 12px rgba(10,37,64,.2);
}
.certificate .meta {
  display: flex; justify-content: space-around; margin: 2rem auto; max-width: 600px;
  font-size: .85rem; color: #6b7280;
}
.certificate .meta .label { text-transform: uppercase; letter-spacing: .05em; font-size: .7rem; margin-bottom: .2rem; }
.certificate .meta .value { color: #0a2540; font-weight: 600; }
.certificate .signatures {
  display: flex; justify-content: space-around; margin: 2.5rem auto; max-width: 600px;
}
.certificate .signatures .sig {
  text-align: center; font-size: .85rem; color: #6b7280;
}
.certificate .signatures .line {
  border-top: 1px solid #1f2937; width: 200px; margin: 2.5rem auto .3rem;
}
.certificate .disclaimer {
  margin-top: 2rem; padding: .8rem; background: #f6f8fc;
  border-left: 3px solid #b08d3e; border-radius: 6px;
  font-size: .72rem; color: #6b7280; text-align: center; max-width: 700px; margin-left: auto; margin-right: auto;
}
"""

CERTIFICATE_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>__CSS__</style></head>
<body>
<div class="certificate">
  <span class="corner tl"></span>
  <span class="corner br"></span>
  <div class="brand">
    <span class="mark">FA</span>
    <span class="name">FinTech Accountant</span>
  </div>
  <div class="eyebrow">Certificate of Completion</div>
  <h1>Certificate of Completion</h1>
  <div class="awarded">This certificate is proudly presented to</div>
  <div class="name">__NAME__</div>
  <div class="course-label">for successfully completing the course</div>
  <div class="course-name">__COURSE__</div>
  <div class="seal">&#10003;</div>
  <div class="meta">
    <div><div class="label">Issue Date</div><div class="value">__DATE__</div></div>
    <div><div class="label">Score</div><div class="value">__SCORE__%</div></div>
    <div><div class="label">Certificate ID</div><div class="value">__CERT_ID__</div></div>
    <div><div class="label">Verification Code</div><div class="value">__CODE__</div></div>
  </div>
  <div class="signatures">
    <div class="sig"><div class="line"></div>Platform Administrator<br><small>FinTech Accountant</small></div>
    <div class="sig"><div class="line"></div>Course Instructor<br><small>__INSTRUCTOR__</small></div>
  </div>
  <div class="disclaimer">__DISCLAIMER__</div>
</div>
</body></html>
"""


def render_certificate_pdf(certificate):
    """Return PDF bytes for a Certificate, or None if WeasyPrint unavailable."""
    if not WEASYPRINT_AVAILABLE:
        logger.warning('WeasyPrint not installed; cannot generate PDF certificate.')
        return None
    try:
        instructor_name = ''
        if certificate.course and certificate.course.instructor:
            instructor_name = certificate.course.instructor.get_full_name()
        html = (CERTIFICATE_HTML
                .replace('__CSS__', CERTIFICATE_CSS)
                .replace('__NAME__', certificate.user.get_full_name() or certificate.user.email)
                .replace('__COURSE__', certificate.course.title if certificate.course else 'Course')
                .replace('__DATE__', certificate.issued_at.strftime('%d %B %Y'))
                .replace('__SCORE__', str(certificate.final_score_pct))
                .replace('__CERT_ID__', certificate.certificate_id)
                .replace('__CODE__', str(certificate.verification_code))
                .replace('__INSTRUCTOR__', instructor_name or 'FinTech Accountant')
                .replace('__DISCLAIMER__', certificate.disclaimer))
        font_config = FontConfiguration()
        pdf = HTML(string=html).write_pdf(font_config=font_config)
        return pdf
    except Exception as e:  # pragma: no cover
        logger.exception('PDF certificate generation failed: %s', e)
        return None
