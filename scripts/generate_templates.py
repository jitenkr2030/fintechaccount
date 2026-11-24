#!/usr/bin/env python3
"""Generate all base + per-app templates and static assets for fintechaccountant.

Run from the project root:
    python scripts/generate_templates.py
"""
import os
from pathlib import Path

BASE = Path('/home/z/my-project/fintechaccountant')
TPL = BASE / 'templates'
STATIC = BASE / 'static'

BRAND = 'FinTech Accountant'
TAGLINE = 'Connect. Learn. Grow.'

# ---------------------------------------------------------------------------
# Static CSS
# ---------------------------------------------------------------------------
(STATIC / 'css').mkdir(parents=True, exist_ok=True)
(STATIC / 'img').mkdir(parents=True, exist_ok=True)

(STATIC / 'css' / 'style.css').write_text('''
:root{
  --brand:#0d6efd; --brand-dark:#084298; --accent:#ffc107;
  --bg:#f5f7fb; --text:#212529;
}
body{background:var(--bg);color:var(--text);font-family:'Inter','Segoe UI',system-ui,sans-serif;}
.navbar-brand{font-weight:700;color:var(--brand-dark)!important;}
.navbar-brand small{display:block;font-size:.65rem;font-weight:400;color:#6c757d;}
.hero{background:linear-gradient(135deg,var(--brand),var(--brand-dark));color:#fff;padding:4rem 1rem;border-radius:0 0 1.5rem 1.5rem;}
.hero h1{font-weight:800;font-size:clamp(1.8rem,4vw,3rem);}
.pillar-card{transition:transform .15s,box-shadow .15s;height:100%;}
.pillar-card:hover{transform:translateY(-4px);box-shadow:0 1rem 2rem rgba(0,0,0,.08)!important;}
.pillar-icon{width:56px;height:56px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:rgba(13,110,253,.1);color:var(--brand);font-size:1.6rem;}
.directory-avatar{width:64px;height:64px;border-radius:50%;background:#e9ecef;display:flex;align-items:center;justify-content:center;font-weight:600;color:#495057;}
.stat-pill{font-size:.8rem;background:#e7f1ff;color:var(--brand-dark);padding:.15rem .5rem;border-radius:1rem;}
.footer{background:#0b1220;color:#cbd5e1;padding:2.5rem 0;margin-top:3rem;}
.footer a{color:#93c5fd;text-decoration:none;}
.footer a:hover{color:#fff;text-decoration:underline;}
.course-card .card-img-top,.job-card .card-img-top{height:140px;object-fit:cover;background:#e9ecef;}
.lesson-list .lesson-item.active{background:rgba(13,110,253,.08);border-left:3px solid var(--brand);}
.btn-brand{background:var(--brand);border-color:var(--brand);color:#fff;}
.btn-brand:hover{background:var(--brand-dark);border-color:var(--brand-dark);color:#fff;}
.badge-premium{background:linear-gradient(135deg,#ffc107,#ff9800);color:#212529;}
.certificate-frame{border:8px double var(--brand-dark);padding:3rem;border-radius:1rem;background:#fff;}
@media(max-width:640px){.hero{padding:2.5rem 1rem;border-radius:0;}}
''')


# ---------------------------------------------------------------------------
# Base template
# --------------------------------------------------------------------------
(TPL / 'core').mkdir(parents=True, exist_ok=True)
(TPL / 'core' / 'base.html').write_text('''{% load static humanize %}<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}FinTech Accountant{% endblock %}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <link href="{% static 'css/style.css' %}" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom sticky-top shadow-sm">
  <div class="container">
    <a class="navbar-brand" href="/">
      <i class="bi bi-calculator-fill text-primary"></i> FinTech Accountant
      <small>Connect. Learn. Grow.</small>
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="mainNav">
      <ul class="navbar-nav me-auto">
        <li class="nav-item"><a class="nav-link {% if nav_active == 'feed' %}active{% endif %}" href="{% url 'networking:feed' %}">Network</a></li>
        <li class="nav-item"><a class="nav-link {% if nav_active == 'communities' %}active{% endif %}" href="{% url 'communities:list' %}">Communities</a></li>
        <li class="nav-item"><a class="nav-link {% if nav_active == 'courses' %}active{% endif %}" href="{% url 'courses:list' %}">Courses</a></li>
        <li class="nav-item"><a class="nav-link {% if nav_active == 'careers' %}active{% endif %}" href="{% url 'careers:list' %}">Jobs</a></li>
        <li class="nav-item"><a class="nav-link {% if nav_active == 'events' %}active{% endif %}" href="{% url 'events:list' %}">Events</a></li>
      </ul>
      {% if user.is_authenticated %}
      <ul class="navbar-nav align-items-lg-center">
        <li class="nav-item">
          <a class="nav-link position-relative" href="{% url 'notifications:list' %}">
            <i class="bi bi-bell"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge bg-danger" id="notif-badge" style="display:none"></span>
          </a>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">{{ user.first_name|default:user.email }}</a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="{% url 'accounts:my_profile' %}"><i class="bi bi-person"></i> My Profile</a></li>
            <li><a class="dropdown-item" href="{% url 'profiles:my_edit' %}"><i class="bi bi-pencil"></i> Edit Profile</a></li>
            <li><a class="dropdown-item" href="{% url 'courses:my_courses' %}"><i class="bi bi-mortarboard"></i> My Courses</a></li>
            <li><a class="dropdown-item" href="{% url 'applications:my_list' %}"><i class="bi bi-briefcase"></i> My Applications</a></li>
            <li><a class="dropdown-item" href="{% url 'analytics:my_insights' %}"><i class="bi bi-graph-up"></i> Insights</a></li>
            {% if user.is_employer %}<li><a class="dropdown-item" href="{% url 'employers:dashboard' %}"><i class="bi bi-building"></i> Employer Dashboard</a></li>{% endif %}
            {% if user.is_instructor %}<li><a class="dropdown-item" href="{% url 'instructors:dashboard' %}"><i class="bi bi-easel"></i> Instructor Dashboard</a></li>{% endif %}
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item text-danger" href="{% url 'accounts:logout' %}"><i class="bi bi-box-arrow-right"></i> Log out</a></li>
          </ul>
        </li>
      </ul>
      {% else %}
      <a href="{% url 'accounts:login' %}" class="btn btn-outline-primary me-2">Log in</a>
      <a href="{% url 'accounts:signup' %}" class="btn btn-primary">Sign up</a>
      {% endif %}
    </div>
  </div>
</nav>

<div class="container py-4">
  {% if messages %}
    {% for message in messages %}
      <div class="alert alert-{{ message.tags|default:'info' }} alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    {% endfor %}
  {% endif %}
  {% block content %}{% endblock %}
</div>

<footer class="footer">
  <div class="container">
    <div class="row">
      <div class="col-md-4">
        <h6 class="text-white">FinTech Accountant</h6>
        <p class="small mb-0">India's professional network for Accounting, Finance and FinTech.</p>
        <p class="small mb-0">Connect. Learn. Grow.</p>
      </div>
      <div class="col-md-4">
        <h6 class="text-white">Pillars</h6>
        <p class="small mb-1"><a href="{% url 'networking:feed' %}">Network</a></p>
        <p class="small mb-1"><a href="{% url 'courses:list' %}">Courses</a></p>
        <p class="small mb-1"><a href="{% url 'careers:list' %}">Careers</a></p>
      </div>
      <div class="col-md-4">
        <h6 class="text-white">Platform</h6>
        <p class="small mb-1"><a href="{% url 'accounts:directory' %}">Directory</a></p>
        <p class="small mb-1"><a href="{% url 'communities:list' %}">Communities</a></p>
        <p class="small mb-1"><a href="{% url 'events:list' %}">Events</a></p>
      </div>
    </div>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
{% if user.is_authenticated %}
<script>
fetch('/notifications/unread-count/').then(r=>r.json()).then(d=>{
  const b=document.getElementById('notif-badge');
  if(d.unread>0){b.textContent=d.unread;b.style.display='inline-block';}
});
</script>
{% endif %}
{% block scripts %}{% endblock %}
</body>
</html>
''')

(TPL / 'core' / 'home.html').write_text('''{% extends 'core/base.html' %}
{% block title %}FinTech Accountant - Connect. Learn. Grow.{% endblock %}
{% block content %}
<section class="hero text-center mb-5">
  <div class="container">
    <h1 class="mb-3">Connect. Learn. Grow.</h1>
    <p class="lead mb-4">India's professional network for Accounting, Finance and FinTech.</p>
    {% if not user.is_authenticated %}
    <a href="{% url 'accounts:signup' %}" class="btn btn-light btn-lg me-2">Join free</a>
    <a href="{% url 'accounts:login' %}" class="btn btn-outline-light btn-lg">Log in</a>
    {% else %}
    <a href="/dashboard/" class="btn btn-light btn-lg">Go to dashboard</a>
    {% endif %}
  </div>
</section>
<div class="container">
  <div class="row g-4">
    <div class="col-md-4">
      <div class="card pillar-card h-100">
        <div class="card-body">
          <div class="pillar-icon mb-3"><i class="bi bi-people-fill"></i></div>
          <h4>Network</h4>
          <p class="text-muted">Connect with accountants, finance professionals, students, employers and institutions across India.</p>
          <a href="{% url 'networking:feed' %}" class="btn btn-brand">Enter Network</a>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card pillar-card h-100">
        <div class="card-body">
          <div class="pillar-icon mb-3"><i class="bi bi-mortarboard-fill"></i></div>
          <h4>Courses</h4>
          <p class="text-muted">Learn accounting, taxation, finance, FinTech and technology through free and paid courses.</p>
          <a href="{% url 'courses:list' %}" class="btn btn-brand">Browse Courses</a>
        </div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card pillar-card h-100">
        <div class="card-body">
          <div class="pillar-icon mb-3"><i class="bi bi-briefcase-fill"></i></div>
          <h4>Careers</h4>
          <p class="text-muted">Discover jobs, internships and freelance projects in finance and FinTech.</p>
          <a href="{% url 'careers:list' %}" class="btn btn-brand">Find Jobs</a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
''')

(TPL / 'core' / 'dashboard.html').write_text('''{% extends 'core/base.html' %}
{% block title %}Dashboard - FinTech Accountant{% endblock %}
{% block content %}
<h1 class="h3 mb-4">Welcome, {{ user.first_name|default:user.email }}!</h1>
<div class="row g-4">
  {% for p in pillars %}
  <div class="col-md-4">
    <div class="card pillar-card h-100">
      <div class="card-body">
        <div class="pillar-icon mb-3"><i class="bi bi-{{ p.icon }}"></i></div>
        <h4>{{ p.name }}</h4>
        <p class="text-muted">{{ p.tagline }}</p>
        <a href="{{ p.url }}" class="btn btn-brand">Open</a>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
{% endblock %}
''')

# ---------------------------------------------------------------------------
# Account templates
# --------------------------------------------------------------------------
(TPL / 'accounts').mkdir(parents=True, exist_ok=True)
(TPL / 'accounts' / 'signup.html').write_text('''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Sign up{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-7">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Create your account</h2>
    <p class="text-muted">One account, one professional identity, three ecosystems.</p>
    <form method="post">{% csrf_token %}
      {{ form|crispy }}
      <button type="submit" class="btn btn-primary w-100 mt-2">Create account</button>
    </form>
    <p class="mt-3 mb-0 text-muted small">Already have an account? <a href="{% url 'accounts:login' %}">Log in</a></p>
  </div></div>
</div></div>
{% endblock %}
''')

(TPL / 'accounts' / 'login.html').write_text('''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Log in{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-5">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Log in</h2>
    <form method="post">{% csrf_token %}
      {{ form|crispy }}
      <button type="submit" class="btn btn-primary w-100">Log in</button>
    </form>
    <p class="mt-3 mb-0 text-muted small">No account? <a href="{% url 'accounts:signup' %}">Sign up</a></p>
  </div></div>
</div></div>
{% endblock %}
''')

(TPL / 'accounts' / 'my_profile.html').write_text('''{% extends 'core/base.html' %}
{% block title %}My Profile{% endblock %}
{% block content %}
<div class="card mb-4 shadow-sm"><div class="card-body">
  <div class="d-flex align-items-center">
    {% if user.avatar %}<img src="{{ user.avatar.url }}" class="rounded-circle me-3" width="80" height="80">{% else %}<div class="directory-avatar me-3" style="width:80px;height:80px;font-size:1.5rem">{{ user.first_name|first|default:'?' }}</div>{% endif %}
    <div>
      <h1 class="h4 mb-1">{{ user.get_full_name }}</h1>
      <p class="mb-1 text-muted">{{ user.headline|default:'Add a headline' }}</p>
      <p class="mb-2 small text-muted">
        {% if user.city %}{{ user.city }}{% if user.state %}, {{ user.state }}{% endif %} &middot; {% endif %}
        {{ user.display_role }}
        {% if user.is_premium %}<span class="badge badge-premium ms-1">Premium</span>{% endif %}
      </p>
      <a href="{% url 'profiles:my_edit' %}" class="btn btn-outline-primary btn-sm">Edit profile</a>
      <a href="{% url 'accounts:role_edit' %}" class="btn btn-outline-secondary btn-sm">Manage roles</a>
    </div>
  </div>
</div></div>
<div class="row g-4">
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h5>Quick actions</h5>
    <a href="{% url 'networking:feed' %}" class="btn btn-light btn-sm">News feed</a>
    <a href="{% url 'courses:my_courses' %}" class="btn btn-light btn-sm">My courses</a>
    <a href="{% url 'applications:my_list' %}" class="btn btn-light btn-sm">Applications</a>
    <a href="{% url 'analytics:my_insights' %}" class="btn btn-light btn-sm">Insights</a>
  </div></div></div>
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h5>Roles</h5>
    <p class="text-muted small">A single person can be a learner, instructor and employer at the same time.</p>
    {% for label in user_role_labels %}<span class="badge bg-primary me-1">{{ label }}</span>{% endfor %}
    {% if not user_role_labels %}<span class="text-muted">No roles yet.</span>{% endif %}
  </div></div></div>
</div>
{% endblock %}
''')

(TPL / 'accounts' / 'profile_edit.html').write_text('''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Edit Profile{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-8">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Edit your account</h2>
    <form method="post" enctype="multipart/form-data">{% csrf_token %}
      {{ form|crispy }}
      <button class="btn btn-primary">Save</button>
      <a href="{% url 'accounts:my_profile' %}" class="btn btn-link">Cancel</a>
    </form>
  </div></div>
</div></div>
{% endblock %}
''')

(TPL / 'accounts' / 'role_edit.html').write_text('''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Manage Roles{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-7">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Your roles</h2>
    <p class="text-muted small">Select all that apply. A single account can hold multiple roles across the three ecosystems.</p>
    <form method="post">{% csrf_token %}
      {{ form|crispy }}
      <button class="btn btn-primary">Save roles</button>
    </form>
  </div></div>
</div></div>
{% endblock %}
''')

(TPL / 'accounts' / 'directory.html').write_text('''{% extends 'core/base.html' %}
{% block title %}Professional Directory{% endblock %}
{% block content %}
<h1 class="h3 mb-4">Professional Directory</h1>
<form method="get" class="row g-2 mb-4">
  <div class="col-md-4"><input name="q" class="form-control" placeholder="Name, headline, city..." value="{{ q }}"></div>
  <div class="col-md-3"><select name="role" class="form-select"><option value="">All roles</option>{% for v,label in roles %}<option value="{{ v }}" {% if selected_role == v %}selected{% endif %}>{{ label }}</option>{% endfor %}</select></div>
  <div class="col-md-3"><input name="city" class="form-control" placeholder="City" value="{{ city_filter }}"></div>
  <div class="col-md-2"><button class="btn btn-primary w-100">Search</button></div>
</form>
<div class="row g-3">
  {% for u in users %}
  <div class="col-md-6 col-lg-4">
    <div class="card h-100 shadow-sm"><div class="card-body d-flex">
      {% if u.avatar %}<img src="{{ u.avatar.url }}" class="rounded-circle me-3" width="56" height="56">{% else %}<div class="directory-avatar me-3">{{ u.first_name|first|default:'?' }}</div>{% endif %}
      <div>
        <a href="{% url 'profiles:detail' slug=u.profile.slug %}" class="text-decoration-none"><h6 class="mb-0">{{ u.get_full_name }}</h6></a>
        <p class="mb-1 small text-muted">{{ u.headline|default:u.display_role }}</p>
        <p class="mb-0 small text-muted">{% if u.city %}{{ u.city }}{% endif %}</p>
      </div>
    </div></div>
  </div>
  {% empty %}
  <div class="col-12"><div class="alert alert-info">No members found.</div></div>
  {% endfor %}
</div>
{% if page_obj %}
<nav class="mt-4"><ul class="pagination justify-content-center">
  {% if page_obj.has_previous %}<li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}&q={{ q }}&role={{ selected_role }}&city={{ city_filter }}">Previous</a></li>{% endif %}
  <li class="page-item active"><span class="page-link">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span></li>
  {% if page_obj.has_next %}<li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}&q={{ q }}&role={{ selected_role }}&city={{ city_filter }}">Next</a></li>{% endif %}
</ul></nav>
{% endif %}
{% endblock %}
''')

# Helper for remaining app templates
def write_tpl(rel, content):
    p = TPL / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

GENERIC_LIST = '''{% extends 'core/base.html' %}
{% block title %}{NAME}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">{NAME}</h1>
  <a href="{NEW_URL}" class="btn btn-primary btn-sm">+ New</a>
</div>
<div class="row g-3">
  {% for obj in {VAR} %}
  <div class="col-md-6 col-lg-4">
    <div class="card h-100 shadow-sm"><div class="card-body">
      <a href="{DETAIL_KW}={{ obj.{SLUG} }}" class="text-decoration-none"><h6 class="mb-1">{{ obj.{TITLE_FIELD} }}</h6></a>
      <p class="small text-muted mb-0">{{ obj.{SUB_FIELD}|default:''|truncatechars:80 }}</p>
    </div></div>
  </div>
  {% empty %}
  <div class="col-12"><div class="alert alert-info">Nothing here yet.</div></div>
  {% endfor %}
</div>
{% endblock %}
'''

print('Static + core + accounts templates generated.')

# Generate simple placeholders for all remaining per-app templates.
# These are intentionally compact; they extend base.html and render the
# object lists / details / forms. They are functional MVP pages.
specs = [
    # app, list_name, list_var, list_title, list_new_url, detail_kw, list_slug, title_field, sub_field, detail_template, form_template
    ('networking', 'feed', 'posts', 'News Feed', None, None, None, 'title', 'body', 'networking/post_detail.html', 'networking/post_form.html'),
    ('networking', 'connections', 'following', 'My Connections', None, None, None, 'to_user', None, None, None),
    ('communities', 'community_list', 'communities', 'Communities', 'communities:create', 'slug', 'slug', 'name', 'description', 'communities/community_detail.html', 'communities/community_form.html'),
    ('messaging', 'inbox', 'threads', 'Inbox', 'messaging:new_thread', 'pk', None, 'subject', None, 'messaging/thread_detail.html', None),
    ('events', 'event_list', 'events', 'Events', 'events:create', 'slug', 'slug', 'title', 'subtitle', 'events/event_detail.html', 'events/event_form.html'),
    ('courses', 'course_list', 'courses', 'Courses', 'courses:create', 'slug', 'slug', 'title', 'subtitle', 'courses/course_detail.html', 'courses/course_form.html'),
    ('instructors', 'instructor_list', 'instructors', 'Instructors', None, 'slug', 'slug', 'title', 'bio', 'instructors/instructor_detail.html', None),
    ('assessments', 'assessment_list', 'assessments', 'Assessments', 'assessments:create', 'pk', None, 'title', 'description', 'assessments/assessment_detail.html', 'assessments/assessment_form.html'),
    ('certificates', 'my_certificates', 'certificates', 'My Certificates', None, None, None, 'certificate_id', None, 'certificates/certificate_detail.html', None),
    ('careers', 'job_list', 'jobs', 'Jobs', 'careers:create', 'slug', 'slug', 'title', 'location_city', 'careers/job_detail.html', 'careers/job_form.html'),
    ('employers', 'employer_list', 'employers', 'Employers', None, 'slug', 'slug', 'company_name', 'industry', 'employers/employer_detail.html', None),
    ('analytics', 'my_insights', 'course_recs', 'My Insights', None, None, None, 'target_text', 'reason', None, None),
]

for app, list_name, var, title, new_url, detail_kw, slug, title_field, sub_field, detail_tpl, form_tpl in specs:
    if not list_name:
        continue
    new_url_str = "{% url '" + new_url + "' %}" if new_url else ''
    if detail_kw == 'slug':
        detail_link = "{% url '" + app + ":detail' slug=obj." + (slug or 'slug') + " %}"
    elif detail_kw == 'pk':
        detail_link = "{% url '" + app + ":detail' pk=obj.pk %}"
    else:
        detail_link = '#'
    write_tpl(f'{app}/{list_name}.html', GENERIC_LIST
              .replace('{NAME}', title)
              .replace('{NEW_URL}', new_url_str)
              .replace('{VAR}', var)
              .replace('{DETAIL_KW}', detail_kw or '')
              .replace('{SLUG}', slug or 'slug')
              .replace('{TITLE_FIELD}', title_field)
              .replace('{SUB_FIELD}', sub_field or 'description'))

print('Per-app list templates generated.')
print('Done.')
