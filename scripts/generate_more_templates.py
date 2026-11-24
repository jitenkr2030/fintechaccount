from pathlib import Path
TPL = Path('templates')

def w(rel, content):
    p = TPL / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

# Generic detail page
DETAIL = '''{% extends 'core/base.html' %}
{% block title %}{{ object.{TITLE} }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <h1 class="h3">{{ object.{TITLE} }}</h1>
  <p class="text-muted">{{ object.{SUB}|default:'' }}</p>
  {% block detail_extra %}{% endblock %}
</div></div>
{% if user.is_authenticated %}
  <a href="{% url '{APP}:create' %}" class="btn btn-outline-primary btn-sm">+ New</a>
{% endif %}
{% endblock %}
'''

# Networking-specific (already mostly generated) - feed and post_detail
w('networking/post_detail.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}{{ post.title|default:post.body|truncatechars:60 }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <div class="d-flex mb-2">
    {% if post.author.avatar %}<img src="{{ post.author.avatar.url }}" class="rounded-circle me-2" width="40" height="40">{% endif %}
    <div>
      <a href="{% url 'profiles:detail' slug=post.author.profile.slug %}" class="text-decoration-none fw-semibold">{{ post.author.get_full_name }}</a>
      <p class="small text-muted mb-0">{{ post.created_at|naturaltime }} · {{ post.get_post_type_display }}</p>
    </div>
  </div>
  {% if post.title %}<h3>{{ post.title }}</h3>{% endif %}
  <p class="mb-2">{{ post.body|linebreaksbr }}</p>
  {% if post.image %}<img src="{{ post.image.url }}" class="img-fluid rounded mb-2">{% endif %}
  {% if post.link_url %}<a href="{{ post.link_url }}" target="_blank" class="d-block text-primary">{{ post.link_url }}</a>{% endif %}
  <div class="d-flex gap-3 mt-2 text-muted small">
    <form method="post" action="{% url 'networking:post_like' post.pk %}" class="d-inline">
      {% csrf_token %}
      <button class="btn btn-sm btn-link text-decoration-none p-0">
        <i class="bi {% if user_liked %}bi-heart-fill text-danger{% else %}bi-heart{% endif %}"></i>
        {{ post.likes_count }} Likes
      </button>
    </form>
    <span><i class="bi bi-chat"></i> {{ post.comments_count }} Comments</span>
  </div>
</div></div>
<h5>Comments</h5>
{% for c in comments %}
  <div class="card mb-2"><div class="card-body p-2">
    <strong>{{ c.author.get_full_name }}</strong> <span class="small text-muted">{{ c.created_at|naturaltime }}</span>
    <p class="mb-0">{{ c.body|linebreaksbr }}</p>
  </div></div>
{% empty %}
  <p class="text-muted">No comments yet.</p>
{% endfor %}
{% if user.is_authenticated %}
<form method="post" action="{% url 'networking:comment_create' post.pk %}">{% csrf_token %}
  {{ comment_form|crispy }}
  <button class="btn btn-primary btn-sm">Comment</button>
</form>
{% endif %}
{% endblock %}
''')

w('networking/feed.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags humanize %}
{% block title %}News Feed{% endblock %}
{% block content %}
<div class="row g-4">
  <div class="col-lg-8">
    {% if user.is_authenticated %}
    <div class="card shadow-sm mb-3"><div class="card-body">
      <form method="post" action="{% url 'networking:post_create' %}" enctype="multipart/form-data">{% csrf_token %}
        {{ post_form|crispy }}
        <button class="btn btn-primary btn-sm">Post</button>
      </form>
    </div></div>
    {% endif %}
    {% for post in posts %}
    <div class="card shadow-sm mb-3"><div class="card-body">
      <div class="d-flex mb-2">
        {% if post.author.avatar %}<img src="{{ post.author.avatar.url }}" class="rounded-circle me-2" width="40" height="40">{% endif %}
        <div>
          <a href="{% url 'profiles:detail' slug=post.author.profile.slug %}" class="text-decoration-none fw-semibold">{{ post.author.get_full_name }}</a>
          <p class="small text-muted mb-0">{{ post.created_at|naturaltime }} · {{ post.get_post_type_display }}</p>
        </div>
      </div>
      <a href="{% url 'networking:post_detail' post.pk %}" class="text-decoration-none text-dark">
        {% if post.title %}<h6 class="mb-1">{{ post.title }}</h6>{% endif %}
        <p class="mb-2">{{ post.body|truncatechars:280|linebreaksbr }}</p>
      </a>
      {% if post.image %}<img src="{{ post.image.url }}" class="img-fluid rounded mb-2">{% endif %}
      <div class="text-muted small"><i class="bi bi-heart"></i> {{ post.likes_count }} &middot; <i class="bi bi-chat"></i> {{ post.comments_count }}</div>
    </div></div>
    {% empty %}
    <div class="alert alert-info">No posts yet. Be the first to share something!</div>
    {% endfor %}
  </div>
  <div class="col-lg-4">
    {% if suggestions %}
    <div class="card shadow-sm mb-3"><div class="card-body">
      <h6 class="mb-3">People you may know</h6>
      {% for s in suggestions %}
      <div class="d-flex align-items-center mb-2">
        <div class="directory-avatar me-2" style="width:36px;height:36px;font-size:.8rem">{{ s.first_name|first|default:'?' }}</div>
        <div class="flex-grow-1">
          <a href="{% url 'profiles:detail' slug=s.profile.slug %}" class="text-decoration-none small fw-semibold">{{ s.get_full_name }}</a>
          <p class="small text-muted mb-0">{{ s.headline|default:s.display_role }}</p>
        </div>
        <form method="post" action="{% url 'networking:connect_toggle' s.id %}">{% csrf_token %}
          <button class="btn btn-sm btn-outline-primary">Follow</button>
        </form>
      </div>
      {% endfor %}
    </div></div>
    {% endif %}
    <div class="card shadow-sm"><div class="card-body">
      <h6 class="mb-2">Trending</h6>
      {% for t in trending %}
      <p class="mb-1 small"><a href="{% url 'networking:post_detail' t.pk %}" class="text-decoration-none">{{ t.title|default:t.body|truncatechars:60 }}</a></p>
      {% empty %}<p class="small text-muted">No trending posts.</p>{% endfor %}
    </div></div>
  </div>
</div>
{% endblock %}
''')

w('networking/connections.html', '''{% extends 'core/base.html' %}
{% block title %}My Connections{% endblock %}
{% block content %}
<h1 class="h3 mb-4">My Connections</h1>
{% if pending %}
<h5>Pending requests</h5>
{% for c in pending %}
<div class="card mb-2"><div class="card-body d-flex align-items-center">
  <div class="flex-grow-1">{{ c.from_user.get_full_name }}</div>
  <form method="post" action="{% url 'networking:connection_action' c.pk 'accept' %}" class="d-inline">{% csrf_token %}<button class="btn btn-sm btn-primary">Accept</button></form>
  <form method="post" action="{% url 'networking:connection_action' c.pk 'decline' %}" class="d-inline">{% csrf_token %}<button class="btn btn-sm btn-link">Decline</button></form>
</div></div>
{% endfor %}
{% endif %}
<h5>Following</h5>
<div class="row g-2">
{% for c in following %}
<div class="col-md-6"><div class="card"><div class="card-body d-flex">
  <div class="flex-grow-1"><a href="{% url 'profiles:detail' slug=c.to_user.profile.slug %}">{{ c.to_user.get_full_name }}</a></div>
</div></div></div>
{% empty %}<p class="text-muted">Not following anyone yet.</p>{% endfor %}
</div>
{% endblock %}
''')

# Messaging
w('messaging/inbox.html', '''{% extends 'core/base.html' %}
{% block title %}Inbox{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">Inbox</h1>
  <a href="{% url 'messaging:new_thread' %}" class="btn btn-primary btn-sm">+ New message</a>
</div>
<div class="list-group">
{% for t in threads %}
<a href="{% url 'messaging:thread_detail' t.pk %}" class="list-group-item list-group-item-action d-flex justify-content-between">
  <div>
    <strong>{{ t.subject|default:'(no subject)' }}</strong>
    <p class="small text-muted mb-0">{% for p in t.participants.all %}{{ p.get_full_name }}{% if not forloop.last %}, {% endif %}{% endfor %}</p>
  </div>
  {% with u=unread|default:'' %}{% if u and u|get_item:t.id %}<span class="badge bg-primary">{{ u|get_item:t.id }} new</span>{% endif %}{% endwith %}
</a>
{% empty %}<div class="alert alert-info">No messages yet.</div>{% endfor %}
</div>
{% endblock %}
''')

w('messaging/thread_detail.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}{{ thread.subject|default:'Conversation' }}{% endblock %}
{% block content %}
<a href="{% url 'messaging:inbox' %}" class="small">&larr; Back to inbox</a>
<h1 class="h4 mb-3">{{ thread.subject|default:'Conversation' }}</h1>
<div class="card mb-3"><div class="card-body" style="max-height:60vh;overflow-y:auto">
{% for m in messages %}
<div class="mb-2 {% if m.sender == user %}text-end{% endif %}">
  <span class="small text-muted">{{ m.sender.get_full_name }} · {{ m.created_at|timesince }} ago</span>
  <div class="d-inline-block bg-light rounded px-3 py-2">{{ m.body|linebreaksbr }}</div>
</div>
{% endfor %}
</div></div>
<form method="post" enctype="multipart/form-data">{% csrf_token %}
  {{ form|crispy }}
  <button class="btn btn-primary">Send</button>
</form>
{% endblock %}
''')

w('messaging/new_thread.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}New message{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-7">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">New message</h2>
    <form method="post">{% csrf_token %}
      {{ form|crispy }}
      <button class="btn btn-primary">Send</button>
    </form>
  </div></div>
</div></div>
{% endblock %}
''')

# Profile templates
w('profiles/profile_detail.html', '''{% extends 'core/base.html' %}
{% block title %}{{ profile.user.get_full_name }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <div class="d-flex">
    {% if profile.user.avatar %}<img src="{{ profile.user.avatar.url }}" class="rounded-circle me-3" width="80" height="80">{% else %}<div class="directory-avatar me-3" style="width:80px;height:80px;font-size:1.5rem">{{ profile.user.first_name|first|default:'?' }}</div>{% endif %}
    <div class="flex-grow-1">
      <h1 class="h4 mb-1">{{ profile.user.get_full_name }}</h1>
      <p class="mb-1 text-muted">{{ profile.user.headline|default:profile.current_title }}</p>
      <p class="mb-2 small text-muted">
        {% if profile.current_company %}{{ profile.current_company }} &middot; {% endif %}
        {% if profile.user.city %}{{ profile.user.city }}{% endif %}
        {% if profile.is_verified_professional %}<span class="badge bg-success ms-1">Verified</span>{% endif %}
        {% if profile.is_open_to_work %}<span class="badge bg-primary ms-1">Open to work</span>{% endif %}
      </p>
      {% if is_owner %}
      <a href="{% url 'profiles:my_edit' %}" class="btn btn-outline-primary btn-sm">Edit</a>
      {% else %}
      <form method="post" action="{% url 'networking:connect_toggle' profile.user.id %}" class="d-inline">{% csrf_token %}
        <button name="kind" value="follow" class="btn btn-primary btn-sm">Follow</button>
        <button name="kind" value="connect" class="btn btn-outline-primary btn-sm">Connect</button>
      </form>
      {% endif %}
    </div>
  </div>
</div></div>
<div class="row g-3">
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h6>Experience</h6>
    {% for e in profile.experiences.all %}<p class="mb-1"><strong>{{ e.title }}</strong> at {{ e.company }}<br><span class="small text-muted">{{ e.start_date }} - {{ e.end_date|default:'Present' }}</span></p>{% empty %}<p class="text-muted small">No experience listed.</p>{% endfor %}
  </div></div></div>
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h6>Education</h6>
    {% for e in profile.educations.all %}<p class="mb-1"><strong>{{ e.degree }}</strong> - {{ e.institution }}<br><span class="small text-muted">{{ e.start_year }} - {{ e.end_date|default:'' }}</span></p>{% empty %}<p class="text-muted small">No education listed.</p>{% endfor %}
  </div></div></div>
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h6>Skills</h6>
    {% for s in profile.skills.all %}<span class="badge bg-light text-dark me-1 mb-1">{{ s.skill.name }} · {{ s.level }}</span>{% empty %}<p class="text-muted small">No skills listed.</p>{% endfor %}
  </div></div></div>
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h6>Certifications</h6>
    {% for c in profile.certifications.all %}<p class="mb-1"><strong>{{ c.name }}</strong> - {{ c.issuing_body }}{% if c.is_statutory %} <span class="badge bg-success">Statutory</span>{% else %} <span class="badge bg-secondary">Course completion</span>{% endif %}</p>{% empty %}<p class="text-muted small">No certifications listed.</p>{% endfor %}
  </div></div></div>
</div>
{% endblock %}
''')

w('profiles/profile_edit.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Edit Professional Profile{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-8">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Professional profile</h2>
    <p class="text-muted small">Profile completion: {{ completion }}%</p>
    <div class="progress mb-3"><div class="progress-bar" style="width:{{ completion }}%"></div></div>
    <form method="post" enctype="multipart/form-data">{% csrf_token %}
      {{ form|crispy }}
      <button class="btn btn-primary">Save</button>
    </form>
    <hr>
    <h6>Add a section</h6>
    <a href="{% url 'profiles:section_add' 'experience' %}" class="btn btn-outline-secondary btn-sm">+ Experience</a>
    <a href="{% url 'profiles:section_add' 'education' %}" class="btn btn-outline-secondary btn-sm">+ Education</a>
    <a href="{% url 'profiles:section_add' 'skill' %}" class="btn btn-outline-secondary btn-sm">+ Skill</a>
    <a href="{% url 'profiles:section_add' 'certification' %}" class="btn btn-outline-secondary btn-sm">+ Certification</a>
    <a href="{% url 'profiles:section_add' 'portfolio' %}" class="btn btn-outline-secondary btn-sm">+ Portfolio</a>
  </div></div>
</div></div>
{% endblock %}
''')

w('profiles/section_form.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Add {{ section_label }}{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-8">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Add {{ section_label }}</h2>
    <form method="post" enctype="multipart/form-data">{% csrf_token %}
      {{ form|crispy }}
      <button class="btn btn-primary">Save</button>
      <a href="{% url 'profiles:my_edit' %}" class="btn btn-link">Cancel</a>
    </form>
  </div></div>
</div></div>
{% endblock %}
''')

w('profiles/section_confirm_delete.html', '''{% extends 'core/base.html' %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-6">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4">Delete this item?</h2>
    <form method="post">{% csrf_token %}<button class="btn btn-danger">Delete</button><a href="{% url 'profiles:my_edit' %}" class="btn btn-link">Cancel</a></form>
  </div></div>
</div></div>
{% endblock %}
''')

w('profiles/resume.html', '''{% extends 'core/base.html' %}
{% block title %}Resume - {{ profile.user.get_full_name }}{% endblock %}
{% block content %}
<div class="card"><div class="card-body">
  <h1>{{ profile.user.get_full_name }}</h1>
  <p class="text-muted">{{ profile.current_title }} · {{ profile.current_company }}</p>
  <hr>
  <h5>Experience</h5>
  {% for e in profile.experiences.all %}<p><strong>{{ e.title }}</strong> at {{ e.company }} ({{ e.start_date }} - {{ e.end_date|default:'Present' }})<br>{{ e.description }}</p>{% endfor %}
  <h5>Education</h5>
  {% for e in profile.educations.all %}<p><strong>{{ e.degree }}</strong>, {{ e.institution }} ({{ e.start_year }} - {{ e.end_year }})</p>{% endfor %}
</div></div>
{% endblock %}
''')

# Course-specific: detail + learn + lesson
w('courses/course_detail.html', '''{% extends 'core/base.html' %}
{% block title %}{{ course.title }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <span class="badge bg-secondary">{{ course.get_level_display }}</span>
  <span class="badge bg-info">{{ course.get_delivery_display }}</span>
  {% if course.is_free %}<span class="badge bg-success">Free</span>{% else %}<span class="badge bg-warning">₹{{ course.effective_price }}</span>{% endif %}
  <h1 class="h3 mt-2">{{ course.title }}</h1>
  <p class="lead text-muted">{{ course.subtitle }}</p>
  <p>{{ course.description|linebreaksbr }}</p>
  {% if course.instructor %}<p class="text-muted">By <a href="{% url 'instructors:detail' slug=course.instructor.instructor_profile.slug %}">{{ course.instructor.get_full_name }}</a></p>{% endif %}
  <p class="text-muted small">{{ course.students_count }} students · {{ course.duration_hours }} hours · Rating {{ course.rating|default:'-' }}/5</p>
  {% if user.is_authenticated %}
    {% if enrollment %}
      <a href="{% url 'courses:learn' slug=course.slug %}" class="btn btn-primary">Continue learning</a>
    {% else %}
      <form method="post" action="{% url 'courses:enroll' slug=course.slug %}">{% csrf_token %}<button class="btn btn-primary">Enroll</button></form>
    {% endif %}
  {% else %}
    <a href="{% url 'accounts:login' %}" class="btn btn-primary">Log in to enroll</a>
  {% endif %}
</div></div>
<h5>Curriculum</h5>
{% for m in modules %}
<div class="card mb-2"><div class="card-body">
  <strong>{{ m.title }}</strong>
  <ul class="mb-0">{% for l in m.lessons %}<li>{{ l.title }} <span class="text-muted small">({{ l.get_content_type_display }}{% if l.duration_minutes %}, {{ l.duration_minutes }}m{% endif %})</span></li>{% endfor %}</ul>
</div></div>
{% empty %}<p class="text-muted">No curriculum yet.</p>{% endfor %}
{% endblock %}
''')

w('courses/learn.html', '''{% extends 'core/base.html' %}
{% block title %}Learning: {{ course.title }}{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h4 mb-0">{{ course.title }}</h1>
  <span class="text-muted small">Progress: {{ enrollment.progress_pct }}%</span>
</div>
<div class="progress mb-3"><div class="progress-bar" style="width:{{ enrollment.progress_pct }}%"></div></div>
{% if first_lesson %}<a href="{% url 'courses:lesson' slug=course.slug pk=first_lesson.pk %}" class="btn btn-primary">Start / Resume</a>{% endif %}
<h6 class="mt-4">Curriculum</h6>
{% for m in modules %}
<div class="card mb-2"><div class="card-body">
  <strong>{{ m.title }}</strong>
  <ul class="mb-0">{% for l in m.lessons %}<li><a href="{% url 'courses:lesson' slug=course.slug pk=l.pk %}">{{ l.title }}</a></li>{% endfor %}</ul>
</div></div>
{% endfor %}
{% endblock %}
''')

w('courses/lesson.html', '''{% extends 'core/base.html' %}
{% block title %}{{ lesson.title }}{% endblock %}
{% block content %}
<a href="{% url 'courses:learn' slug=course.slug %}" class="small">&larr; Back to course</a>
<h1 class="h4">{{ lesson.title }}</h1>
{% if lesson.video_url %}
<div class="ratio ratio-16x9 mb-3"><iframe src="{{ lesson.video_url }}" allowfullscreen></iframe></div>
{% endif %}
<p>{{ lesson.body|linebreaksbr }}</p>
{% if enrollment %}
<form method="post" action="{% url 'courses:lesson_complete' slug=course.slug pk=lesson.pk %}">{% csrf_token %}
  <button class="btn btn-success btn-sm">{% if progress.is_completed %}Completed ✓{% else %}Mark complete{% endif %}</button>
</form>
{% endif %}
{% endblock %}
''')

w('courses/my_courses.html', '''{% extends 'core/base.html' %}
{% block title %}My Courses{% endblock %}
{% block content %}
<h1 class="h3 mb-4">My Courses</h1>
<div class="row g-3">
{% for e in enrollments %}
<div class="col-md-6 col-lg-4"><div class="card h-100 shadow-sm"><div class="card-body">
  <a href="{% url 'courses:learn' slug=e.course.slug %}" class="text-decoration-none"><h6>{{ e.course.title }}</h6></a>
  <p class="small text-muted mb-1">{{ e.get_status_display }}</p>
  <div class="progress"><div class="progress-bar" style="width:{{ e.progress_pct }}%"></div></div>
</div></div></div>
{% empty %}<div class="col-12"><div class="alert alert-info">You are not enrolled in any course yet. <a href="{% url 'courses:list' %}">Browse courses</a></div></div>{% endfor %}
</div>
{% endblock %}
''')

# Certificate printable
w('certificates/certificate_detail.html', '''{% extends 'core/base.html' %}
{% block title %}Certificate {{ certificate.certificate_id }}{% endblock %}
{% block content %}
<div class="certificate-frame text-center">
  <h6 class="text-muted">FinTech Accountant - Certificate of Completion</h6>
  <h1>{{ certificate.user.get_full_name }}</h1>
  <p>has successfully completed</p>
  <h3>{{ certificate.course.title }}</h3>
  <p class="text-muted">Issued on {{ certificate.issued_at|date:"j F Y" }} · Score: {{ certificate.final_score_pct }}%</p>
  <p class="small text-muted">Certificate ID: {{ certificate.certificate_id }}</p>
  <hr>
  <p class="small text-muted">{{ certificate.disclaimer }}</p>
</div>
{% endblock %}
''')

w('certificates/printable.html', '''{% extends 'core/base.html' %}
{% block title %}Certificate {{ certificate.certificate_id }}{% endblock %}
{% block content %}
<div class="certificate-frame text-center">
  <h6 class="text-muted">FinTech Accountant - Certificate of Completion</h6>
  <h1>{{ certificate.user.get_full_name }}</h1>
  <p>has successfully completed</p>
  <h3>{{ certificate.course.title }}</h3>
  <p class="text-muted">Issued on {{ certificate.issued_at|date:"j F Y" }} · Score: {{ certificate.final_score_pct }}%</p>
  <p class="small text-muted">Certificate ID: {{ certificate.certificate_id }} · Code: {{ certificate.verification_code }}</p>
  <hr>
  <p class="small text-muted">{{ certificate.disclaimer }}</p>
  <button onclick="window.print()" class="btn btn-outline-primary btn-sm">Print / Save as PDF</button>
</div>
{% endblock %}
''')

w('certificates/verify.html', '''{% extends 'core/base.html' %}
{% block title %}Verify Certificate{% endblock %}
{% block content %}
<h1 class="h3 mb-4">Verify a Certificate</h1>
<div class="row justify-content-center"><div class="col-md-6">
  <div class="card shadow-sm"><div class="card-body p-4">
    <form method="post">{% csrf_token %}
      <div class="mb-2"><label class="form-label">Certificate ID</label><input name="certificate_id" class="form-control" value="{{ request.POST.certificate_id|default:'' }}"></div>
      <div class="mb-3"><label class="form-label">Verification code</label><input name="verification_code" class="form-control" value="{{ request.POST.verification_code|default:'' }}"></div>
      <button class="btn btn-primary w-100">Verify</button>
    </form>
    {% if submitted %}
      <hr>
      {% if valid and certificate %}
        <div class="alert alert-success">Valid certificate.<br><strong>{{ certificate.user.get_full_name }}</strong> completed <strong>{{ certificate.course.title }}</strong>.</div>
      {% else %}
        <div class="alert alert-danger">Invalid certificate or code.</div>
      {% endif %}
    {% endif %}
  </div></div>
</div></div>
{% endblock %}
''')

# Career: job_detail, apply, my list, employer jobs, alerts
w('careers/job_detail.html', '''{% extends 'core/base.html' %}
{% block title %}{{ job.title }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <h1 class="h3">{{ job.title }}</h1>
  {% if job.employer %}<p class="text-muted"><a href="{% url 'employers:detail' slug=job.employer.slug %}">{{ job.employer.company_name }}</a></p>{% endif %}
  <p class="text-muted small">
    <span class="badge bg-secondary">{{ job.get_employment_type_display }}</span>
    <span class="badge bg-info">{{ job.get_experience_level_display }}</span>
    {% if job.is_remote %}<span class="badge bg-success">Remote</span>{% endif %}
    {% if job.is_wfh %}<span class="badge bg-primary">WFH</span>{% endif %}
    {% if job.is_featured %}<span class="badge bg-warning">Featured</span>{% endif %}
  </p>
  <p class="mb-2"><i class="bi bi-geo-alt"></i> {{ job.location_city|default:'-' }} · Salary: {{ job.salary_range }}</p>
  <h6>Description</h6><p>{{ job.description|linebreaksbr }}</p>
  {% if job.requirements %}<h6>Requirements</h6><p>{{ job.requirements|linebreaksbr }}</p>{% endif %}
  {% if job.responsibilities %}<h6>Responsibilities</h6><p>{{ job.responsibilities|linebreaksbr }}</p>{% endif %}
  {% if job.skills_required %}<p><strong>Skills:</strong> {{ job.skills_required }}</p>{% endif %}
  <p class="small text-muted">Posted {{ job.posted_at|naturaltime }} · {{ job.applications_count }} applicants</p>
  {% if user.is_authenticated %}
    {% if user_application %}
      <span class="badge bg-info">You applied ({{ user_application.get_status_display }})</span>
    {% else %}
      <a href="{% url 'applications:apply' slug=job.slug %}" class="btn btn-primary">Apply now</a>
    {% endif %}
  {% else %}
    <a href="{% url 'accounts:login' %}" class="btn btn-primary">Log in to apply</a>
  {% endif %}
</div></div>
{% endblock %}
''')

# Applications
w('applications/apply.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Apply: {{ job.title }}{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-8">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-1">Apply for: {{ job.title }}</h2>
    <p class="text-muted small">{{ job.employer.company_name|default:'' }}</p>
    <form method="post" enctype="multipart/form-data">{% csrf_token %}
      {{ form|crispy }}
      <button class="btn btn-primary">Submit application</button>
      <a href="{% url 'careers:detail' slug=job.slug %}" class="btn btn-link">Cancel</a>
    </form>
  </div></div>
</div></div>
{% endblock %}
''')

w('applications/my_applications.html', '''{% extends 'core/base.html' %}
{% block title %}My Applications{% endblock %}
{% block content %}
<h1 class="h3 mb-4">My Applications</h1>
<div class="list-group">
{% for a in applications %}
<a href="{% url 'applications:my_detail' a.pk %}" class="list-group-item list-group-item-action">
  <div class="d-flex justify-content-between">
    <div><strong>{{ a.job.title }}</strong><br><span class="small text-muted">{{ a.job.employer.company_name|default:'' }}</span></div>
    <span class="badge bg-secondary">{{ a.get_status_display }}</span>
  </div>
</a>
{% empty %}<div class="alert alert-info">No applications yet. <a href="{% url 'careers:list' %}">Browse jobs</a></div>{% endfor %}
</div>
{% endblock %}
''')

w('applications/application_detail.html', '''{% extends 'core/base.html' %}
{% block title %}Application: {{ application.job.title }}{% endblock %}
{% block content %}
<a href="{% url 'applications:my_list' %}" class="small">&larr; Back</a>
<h1 class="h4">{{ application.job.title }}</h1>
<p class="text-muted">Status: <span class="badge bg-secondary">{{ application.get_status_display }}</span></p>
<p><strong>Cover letter:</strong><br>{{ application.cover_letter|linebreaksbr }}</p>
{% if application.resume %}<p><a href="{{ application.resume.url }}">View resume</a></p>{% endif %}
{% if is_applicant %}
  {% if application.status != 'withdrawn' %}
  <form method="post" action="{% url 'applications:withdraw' application.pk %}">{% csrf_token %}<button class="btn btn-outline-danger btn-sm">Withdraw</button></form>
  {% endif %}
{% elif is_employer %}
  <form method="post" action="{% url 'applications:update_status' application.pk %}" class="d-inline">{% csrf_token %}
    <select name="status" class="form-select form-select-sm d-inline-block" style="width:auto">
      {% for s,label in application.STATUSES %}<option value="{{ s }}" {% if application.status == s %}selected{% endif %}>{{ label }}</option>{% endfor %}
    </select>
    <button class="btn btn-primary btn-sm">Update</button>
  </form>
{% endif %}
{% endblock %}
''')

w('applications/job_applications.html', '''{% extends 'core/base.html' %}
{% block title %}Applicants: {{ job.title }}{% endblock %}
{% block content %}
<h1 class="h4">Applicants for: {{ job.title }}</h1>
<div class="list-group mt-3">
{% for a in applications %}
<a href="{% url 'applications:my_detail' a.pk %}" class="list-group-item list-group-item-action">
  <div class="d-flex justify-content-between">
    <div><strong>{{ a.applicant.get_full_name }}</strong><br><span class="small text-muted">{{ a.applicant.headline|default:'' }}</span></div>
    <span class="badge bg-secondary">{{ a.get_status_display }}</span>
  </div>
</a>
{% empty %}<div class="alert alert-info">No applications yet.</div>{% endfor %}
</div>
{% endblock %}
''')

# Employer: detail, dashboard, become, edit, candidate_search
w('employers/employer_detail.html', '''{% extends 'core/base.html' %}
{% block title %}{{ employer.company_name }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <div class="d-flex">
    {% if employer.logo %}<img src="{{ employer.logo.url }}" class="rounded me-3" width="80" height="80">{% endif %}
    <div><h1 class="h3">{{ employer.company_name }}</h1><p class="text-muted">{{ employer.tagline }}</p><p class="small text-muted">{{ employer.industry }} · {{ employer.company_size }} · {{ employer.headquarters_city }}</p></div>
  </div>
  <p>{{ employer.about|linebreaksbr }}</p>
</div></div>
<h5>Open jobs</h5>
{% for j in jobs %}<p><a href="{% url 'careers:detail' slug=j.slug %}">{{ j.title }}</a></p>{% empty %}<p class="text-muted">No open jobs.</p>{% endfor %}
{% endblock %}
''')

w('employers/become_employer.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block title %}Become an Employer{% endblock %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-7">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Set up your employer profile</h2>
    <form method="post">{% csrf_token %}{{ form|crispy }}<button class="btn btn-primary">Create</button></form>
  </div></div>
</div></div>
{% endblock %}
''')

w('employers/employer_edit.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-8">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Edit company profile</h2>
    <form method="post" enctype="multipart/form-data">{% csrf_token %}{{ form|crispy }}<button class="btn btn-primary">Save</button></form>
  </div></div>
</div></div>
{% endblock %}
''')

w('employers/dashboard.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-4">Employer Dashboard</h1>
{% if employer %}
<div class="row g-3 mb-4">
  <div class="col-md-4"><div class="card text-center"><div class="card-body"><h3>{{ employer.jobs_count|default:employer.jobs.count }}</h3><p class="text-muted mb-0">Jobs posted</p></div></div></div>
  <div class="col-md-4"><div class="card text-center"><div class="card-body"><h3>{{ recent_applications|length }}</h3><p class="text-muted mb-0">Recent applications</p></div></div></div>
  <div class="col-md-4"><div class="card text-center"><div class="card-body"><h3>{{ employer.hires_count }}</h3><p class="text-muted mb-0">Hires</p></div></div></div>
</div>
<div class="d-flex gap-2 mb-3">
  <a href="{% url 'careers:create' %}" class="btn btn-primary">+ Post a job</a>
  <a href="{% url 'employers:candidate_search' %}" class="btn btn-outline-primary">Search candidates</a>
  <a href="{% url 'employers:edit' %}" class="btn btn-outline-secondary">Edit profile</a>
</div>
<h5>Recent applications</h5>
<div class="list-group">
{% for a in recent_applications %}
<a href="{% url 'applications:my_detail' a.pk %}" class="list-group-item list-group-item-action">
  {{ a.applicant.get_full_name }} applied to <strong>{{ a.job.title }}</strong>
  <span class="badge bg-secondary float-end">{{ a.get_status_display }}</span>
</a>
{% empty %}<div class="alert alert-info">No applications yet.</div>{% endfor %}
</div>
{% else %}
<p>You don't have an employer profile yet.</p>
<a href="{% url 'employers:become' %}" class="btn btn-primary">Become an employer</a>
{% endif %}
{% endblock %}
''')

w('employers/candidate_search.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-3">Search Candidates</h1>
<form method="get" class="mb-3"><input name="q" class="form-control" placeholder="Name, title, industry, headline..." value="{{ q }}"></form>
<div class="row g-3">
{% for p in profiles %}
<div class="col-md-6 col-lg-4"><div class="card h-100"><div class="card-body">
  <a href="{% url 'profiles:detail' slug=p.slug %}">{{ p.user.get_full_name }}</a>
  <p class="small text-muted mb-0">{{ p.current_title|default:p.user.headline }} · {{ p.industry|default:'' }}</p>
</div></div></div>
{% empty %}<div class="col-12"><div class="alert alert-info">No candidates found.</div></div>{% endfor %}
</div>
{% endblock %}
''')

# Instructor: detail, dashboard, become, edit
w('instructors/instructor_detail.html', '''{% extends 'core/base.html' %}
{% block title %}{{ instructor.title }}{% endblock %}
{% block content %}
<div class="card shadow-sm mb-3"><div class="card-body">
  <h1 class="h3">{{ instructor.user.get_full_name }}</h1>
  <p class="text-muted">{{ instructor.title }}</p>
  <p>{{ instructor.bio|linebreaksbr }}</p>
  <p class="small text-muted">{{ instructor.students_count }} students · {{ instructor.courses_count }} courses · Rating {{ instructor.avg_rating|default:'-' }}</p>
</div></div>
<h5>Courses by {{ instructor.user.first_name }}</h5>
{% for c in courses %}<p><a href="{% url 'courses:detail' slug=c.slug %}">{{ c.title }}</a> <span class="text-muted small">({{ c.students_count }} students)</span></p>{% empty %}<p class="text-muted">No courses yet.</p>{% endfor %}
{% endblock %}
''')

w('instructors/become_instructor.html', '''{% extends 'core/base.html' %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-7">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Become an instructor</h2>
    <form method="post">{% csrf_token %}
      <div class="mb-2"><label class="form-label">Title</label><input name="title" class="form-control" placeholder="e.g. CA, Senior Accountant, GST Expert"></div>
      <div class="mb-2"><label class="form-label">Bio</label><textarea name="bio" class="form-control" rows="3"></textarea></div>
      <div class="mb-3"><label class="form-label">Expertise</label><input name="expertise" class="form-control" placeholder="GST, IFRS, FinTech"></div>
      <button class="btn btn-primary">Become an instructor</button>
    </form>
  </div></div>
</div></div>
{% endblock %}
''')

w('instructors/instructor_edit.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-8">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Instructor profile</h2>
    <form method="post" enctype="multipart/form-data">{% csrf_token %}{{ form|crispy }}<button class="btn btn-primary">Save</button></form>
  </div></div>
</div></div>
{% endblock %}
''')

w('instructors/dashboard.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-4">Instructor Dashboard</h1>
{% if profile %}
<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ profile.courses_count|default:courses|length }}</h3><p class="text-muted mb-0">Courses</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ total_students }}</h3><p class="text-muted mb-0">Students</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>₹{{ pending_payout|floatformat:0 }}</h3><p class="text-muted mb-0">Pending payout</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ profile.avg_rating|default:'-' }}</h3><p class="text-muted mb-0">Avg rating</p></div></div></div>
</div>
<div class="d-flex gap-2 mb-3">
  <a href="{% url 'courses:create' %}" class="btn btn-primary">+ Create course</a>
  <a href="{% url 'instructors:edit' %}" class="btn btn-outline-secondary">Edit profile</a>
</div>
<h5>Your courses</h5>
{% for c in courses %}<p><a href="{% url 'courses:detail' slug=c.slug %}">{{ c.title }}</a> <span class="text-muted small">({{ c.students_count }} students, {{ c.status }})</span></p>{% endfor %}
{% else %}
<p>You don't have an instructor profile yet.</p>
<a href="{% url 'instructors:become' %}" class="btn btn-primary">Become an instructor</a>
{% endif %}
{% endblock %}
''')

# Assessments: take, result
w('assessments/take.html', '''{% extends 'core/base.html' %}
{% block title %}{{ assessment.title }}{% endblock %}
{% block content %}
<div class="card shadow-sm"><div class="card-body">
  <h1 class="h3">{{ assessment.title }}</h1>
  <p class="text-muted">Duration: {{ assessment.duration_minutes }} minutes · Passing: {{ assessment.passing_score_pct }}%</p>
  <form method="post">{% csrf_token %}
    {% for field in form %}
      <div class="mb-3">
        <label class="form-label fw-semibold">{{ field.label }}</label>
        {{ field }}
      </div>
    {% endfor %}
    <button class="btn btn-primary">Submit assessment</button>
  </form>
</div></div>
{% endblock %}
''')

w('assessments/result.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3">{{ assessment.title }}</h1>
<p>Your latest attempt: <strong>{{ latest.score_pct }}%</strong> - {% if latest.is_passed %}<span class="badge bg-success">Passed</span>{% else %}<span class="badge bg-danger">Failed</span>{% endif %}</p>
<p class="text-muted">Status: {{ latest.get_status_display }}</p>
{% for a in attempts %}
<div class="card mb-2"><div class="card-body small">{{ a.score_pct }}% on {{ a.started_at|date:'j M Y H:i' }} - {{ a.get_status_display }}</div></div>
{% endfor %}
{% endblock %}
''')

w('assessments/question_form.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<div class="card shadow-sm"><div class="card-body p-4">
  <h2 class="h4 mb-3">Add Question - {{ assessment.title }}</h2>
  <form method="post">{% csrf_token %}
    {{ form|crispy }}
    <h6>Choices</h6>
    {{ choice_formset.management_form }}
    {% for f in choice_formset %}{{ f|crispy }}{% endfor %}
    <button class="btn btn-primary">Save question</button>
    <a href="{% url 'assessments:detail' assessment.pk %}" class="btn btn-link">Done</a>
  </form>
</div></div>
{% endblock %}
''')

w('assessments/assessment_detail.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3">{{ assessment.title }}</h1>
<p class="text-muted">{{ assessment.description }}</p>
<p>Duration: {{ assessment.duration_minutes }} mins · Passing: {{ assessment.passing_score_pct }}% · Max attempts: {{ assessment.max_attempts }}</p>
{% if user.is_authenticated %}
<a href="{% url 'assessments:take' assessment.pk %}" class="btn btn-primary">Start attempt</a>
{% endif %}
<h6 class="mt-4">Questions ({{ questions|length }})</h6>
{% for q in questions %}<p>{{ forloop.counter }}. {{ q.body }} <span class="text-muted">({{ q.marks }} marks)</span></p>{% endfor %}
<h6 class="mt-4">Your attempts</h6>
{% for a in attempts %}<p>{{ a.score_pct }}% - {{ a.get_status_display }} ({{ a.started_at }})</p>{% empty %}<p class="text-muted">No attempts yet.</p>{% endfor %}
{% endblock %}
''')

# Notifications
w('notifications/notification_list.html', '''{% extends 'core/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">Notifications</h1>
  <form method="post" action="{% url 'notifications:mark_all_read' %}">{% csrf_token %}<button class="btn btn-outline-secondary btn-sm">Mark all read</button></form>
</div>
{% for a in announcements %}
<div class="alert alert-info"><strong>{{ a.title }}</strong><br>{{ a.body|truncatechars:200 }}</div>
{% endfor %}
<div class="list-group">
{% for n in notifications %}
<div class="list-group-item list-group-item-action {% if not n.is_read %}list-group-item-primary{% endif %}">
  <div class="d-flex justify-content-between">
    <div><strong>{% if n.actor %}{{ n.actor.get_full_name }}{% else %}System{% endif %}</strong> {{ n.verb }}
      {% if n.target_text %}<a href="{{ n.target_url }}">{{ n.target_text }}</a>{% endif %}
    </div>
    <span class="small text-muted">{{ n.created_at|naturaltime }}</span>
  </div>
</div>
{% empty %}<div class="alert alert-info">No notifications.</div>{% endfor %}
</div>
{% endblock %}
''')

# Moderation
w('moderation/report_form.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-7">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Report content</h2>
    <form method="post">{% csrf_token %}{{ form|crispy }}<button class="btn btn-warning">Submit report</button></form>
  </div></div>
</div></div>
{% endblock %}
''')

w('moderation/my_reports.html', '''{% extends 'core/base.html' %}
{% block content %}<h1 class="h3 mb-3">My Reports</h1>
<div class="list-group">{% for r in reports %}<div class="list-group-item"><strong>{{ r.get_target_type_display }} #{{ r.target_id }}</strong> - {{ r.get_reason_display }} <span class="badge bg-secondary">{{ r.get_status_display }}</span></div>{% empty %}<div class="alert alert-info">No reports.</div>{% endfor %}</div>
{% endblock %}
''')

w('moderation/queue.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-3">Moderation Queue ({{ pending_count }} pending)</h1>
<form method="get" class="mb-3"><select name="status" class="form-select" style="width:auto;display:inline-block"><option value="">All statuses</option>{% for s,label in statuses %}<option value="{{ s }}" {% if selected_status == s %}selected{% endif %}>{{ label }}</option>{% endfor %}</select><button class="btn btn-outline-primary btn-sm">Filter</button></form>
<div class="list-group">{% for r in reports %}<a href="{% url 'moderation:report_detail' r.pk %}" class="list-group-item list-group-item-action"><strong>{{ r.get_target_type_display }} #{{ r.target_id }}</strong> - {{ r.get_reason_display }} <span class="badge bg-secondary float-end">{{ r.get_status_display }}</span></a>{% empty %}<div class="alert alert-success">No reports. All clear!</div>{% endfor %}</div>
{% endblock %}
''')

w('moderation/report_detail.html', '''{% extends 'core/base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<h1 class="h4">Report #{{ report.pk }}</h1>
<p><strong>Target:</strong> {{ report.get_target_type_display }} #{{ report.target_id }}<br><strong>Reason:</strong> {{ report.get_reason_display }}<br><strong>Status:</strong> {{ report.get_status_display }}<br><strong>Description:</strong> {{ report.description }}</p>
{% if report.target_url %}<p><a href="{{ report.target_url }}" target="_blank">View reported content</a></p>{% endif %}
<h6>Take action</h6>
<form method="post" action="{% url 'moderation:take_action' report.pk %}">{% csrf_token %}{{ action_form|crispy }}<button class="btn btn-primary">Take action</button></form>
{% if actions %}<h6 class="mt-3">Previous actions</h6>{% for a in actions %}<p class="small">{{ a.admin|default:'Admin' }} {{ a.get_action_display }} on {{ a.created_at|date:'j M Y' }}</p>{% endfor %}{% endif %}
{% endblock %}
''')

# Payments
w('payments/checkout.html', '''{% extends 'core/base.html' %}
{% block content %}
<div class="row justify-content-center"><div class="col-md-6">
  <div class="card shadow-sm"><div class="card-body p-4">
    <h2 class="h4 mb-3">Checkout</h2>
    <p class="text-muted">{{ order.description }}</p>
    <p><strong>Amount:</strong> ₹{{ order.amount }} {{ order.currency }}</p>
    {% if rp_mock %}
      <div class="alert alert-warning small">Razorpay is not configured (mock mode). Use any test payment id to complete the order.</div>
      <form method="post" action="{% url 'payments:verify' order.razorpay_order_id %}">
        {% csrf_token %}
        <input type="hidden" name="razorpay_payment_id" value="mock_payment_{{ order.id }}">
        <input type="hidden" name="razorpay_signature" value="mock_signature">
        <button class="btn btn-primary w-100">Complete (mock) payment</button>
      </form>
    {% else %}
      <button id="rzp-button" class="btn btn-primary w-100">Pay ₹{{ order.amount }} with Razorpay</button>
      <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
      <script>
      var options = { key: "{{ rp_key_id }}", amount: {{ amount_paise }}, currency: "{{ currency }}",
        name: "FinTech Accountant", order_id: "{{ rp_order_id }}",
        handler: function (resp){
          var f = document.createElement('form'); f.method='POST'; f.action='{% url "payments:verify" order.razorpay_order_id %}';
          var csrf = document.createElement('input'); csrf.type='hidden'; csrf.name='csrfmiddlewaretoken'; csrf.value='{{ csrf_token }}';
          var p = document.createElement('input'); p.type='hidden'; p.name='razorpay_payment_id'; p.value=resp.razorpay_payment_id;
          var s = document.createElement('input'); s.type='hidden'; s.name='razorpay_signature'; s.value=resp.razorpay_signature;
          f.appendChild(csid); f.appendChild(p); f.appendChild(s); document.body.appendChild(f); f.submit();
        }
      };
      var rzp = new Razorpay(options); document.getElementById('rzp-button').onclick = function(e){ rzp.open(); e.preventDefault(); };
      </script>
    {% endif %}
  </div></div>
</div></div>
{% endblock %}
''')

w('payments/history.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-4">Payment History</h1>
<h5>Orders</h5>
<div class="list-group mb-4">{% for o in orders %}<div class="list-group-item"><strong>₹{{ o.amount }}</strong> {{ o.get_content_type_label_display }} <span class="badge bg-secondary">{{ o.get_status_display }}</span> <span class="small text-muted">{{ o.created_at|date:'j M Y H:i' }}</span></div>{% empty %}<div class="alert alert-info">No orders.</div>{% endfor %}</div>
<h5>Subscriptions</h5>
<div class="list-group">{% for s in subscriptions %}<div class="list-group-item">{{ s.get_subscription_type_display }} - ₹{{ s.amount }} <span class="badge bg-secondary">{{ s.get_status_display }}</span> <span class="small text-muted">until {{ s.current_period_end|date:'j M Y' }}</span></div>{% empty %}<div class="alert alert-info">No subscriptions.</div>{% endfor %}</div>
{% endblock %}
''')

# Analytics
w('analytics/my_insights.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-4">Your Insights</h1>
<div class="row g-3">
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h5>Recommended courses</h5>
    {% for r in course_recs %}<p class="mb-1"><a href="{{ r.target_url }}">{{ r.target_text }}</a> <span class="small text-muted">{{ r.reason }}</span></p>{% empty %}<p class="text-muted small">No recommendations yet. Complete your profile to get suggestions.</p>{% endfor %}
  </div></div></div>
  <div class="col-md-6"><div class="card h-100 shadow-sm"><div class="card-body">
    <h5>Recommended jobs</h5>
    {% for r in job_recs %}<p class="mb-1"><a href="{{ r.target_url }}">{{ r.target_text }}</a> <span class="small text-muted">{{ r.reason }}</span></p>{% empty %}<p class="text-muted small">No recommendations yet. Add skills to your profile to get matched.</p>{% endfor %}
  </div></div></div>
</div>
{% endblock %}
''')

w('analytics/admin_dashboard.html', '''{% extends 'core/base.html' %}
{% block content %}
<h1 class="h3 mb-4">Platform Analytics</h1>
<div class="row g-3 mb-4">
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ total_users }}</h3><p class="text-muted mb-0">Users</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ total_courses }}</h3><p class="text-muted mb-0">Courses</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ total_jobs }}</h3><p class="text-muted mb-0">Open jobs</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>₹{{ revenue|floatformat:0 }}</h3><p class="text-muted mb-0">Revenue</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ total_enrollments }}</h3><p class="text-muted mb-0">Enrollments</p></div></div></div>
  <div class="col-md-3"><div class="card text-center"><div class="card-body"><h3>{{ total_applications }}</h3><p class="text-muted mb-0">Applications</p></div></div></div>
</div>
<h5>Recent users</h5>
<div class="list-group mb-3">{% for u in recent_users %}<div class="list-group-item">{{ u.email }} - {{ u.get_full_name }} <span class="small text-muted">{{ u.date_joined }}</span></div>{% endfor %}</div>
<h5>Recent payments</h5>
<div class="list-group">{% for o in recent_orders %}<div class="list-group-item">₹{{ o.amount }} {{ o.get_content_type_label_display }} - {{ o.user.email }} <span class="small text-muted">{{ o.paid_at }}</span></div>{% empty %}<div class="alert alert-info">No payments yet.</div>{% endfor %}</div>
{% endblock %}
''')

# Career: employer_jobs, my_alerts, alert_form, job_confirm_delete
w('careers/employer_jobs.html', '''{% extends 'core/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">My Job Postings</h1>
  <a href="{% url 'careers:create' %}" class="btn btn-primary btn-sm">+ Post a job</a>
</div>
<div class="list-group">{% for j in jobs %}<a href="{% url 'careers:detail' slug=j.slug %}" class="list-group-item list-group-item-action"><div class="d-flex justify-content-between"><div><strong>{{ j.title }}</strong><br><span class="small text-muted">{{ j.location_city }} · {{ j.get_employment_type_display }}</span></div><div><span class="badge bg-secondary">{{ j.get_status_display }}</span> <span class="badge bg-info">{{ j.applications_count }} applicants</span></div></div></a>{% empty %}<div class="alert alert-info">No jobs posted yet.</div>{% endfor %}</div>
{% endblock %}
''')

w('careers/my_alerts.html', '''{% extends 'core/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
  <h1 class="h3 mb-0">My Job Alerts</h1>
  <a href="{% url 'careers:alert_create' %}" class="btn btn-primary btn-sm">+ New alert</a>
</div>
<div class="list-group">{% for a in alerts %}<div class="list-group-item"><div class="d-flex justify-content-between"><div><strong>{{ a.keywords|default:'Any keyword' }}</strong> <span class="small text-muted">{{ a.location_city|default:'' }} · {{ a.get_frequency_display }}</span></div><form method="post" action="{% url 'careers:alert_toggle' a.pk %}">{% csrf_token %}<button class="btn btn-sm {% if a.is_active %}btn-outline-secondary{% else %}btn-primary{% endif %}">{% if a.is_active %}Pause{% else %}Activate{% endif %}</button></form></div></div>{% empty %}<div class="alert alert-info">No alerts.</div>{% endfor %}</div>
{% endblock %}
''')

print('All per-app templates generated.')
