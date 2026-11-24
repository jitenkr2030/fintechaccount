# FinTech Accountant

**India's professional network for Accounting, Finance and FinTech.**
**Connect. Learn. Grow.**

A unified professional platform combining elements of LinkedIn, Coursera and a
finance-sector job portal — three connected ecosystems with a shared user
identity:

- **Network** — professional profiles, news feed, connections, communities, messaging, events, mentorship, Q&A
- **Courses** — LMS with catalog, lessons, enrollment, progress, assessments, certificates, payments
- **Careers** — jobs, internships, freelance projects, applications, employer profiles, recruitment, credential verification

Built as a Django modular monolith covering all 5 phases of the development roadmap.

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env          # then edit SECRET_KEY etc.

# 3. Run migrations
python manage.py migrate

# 5. Seed roles + demo data
python manage.py shell -c "exec(open('scripts/seed.py').read()); run()"

# 6. Run the server
python manage.py runserver
```

Open <http://127.0.0.1:8000/>

### Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@fintechaccountant.com | admin123 |
| Student | student@demo.in | demo1234 |
| Professional (CA) | ca@demo.in | demo1234 |
| Instructor (CMA) | instructor@demo.in | demo1234 |
| Instructor (GST) | rajesh@demo.in | demo1234 |
| Employer (Acme Corp) | hr@acme.in | demo1234 |
| Employer (Finovate) | careers@finovate.in | demo1234 |

---

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Django 5.2 |
| API | Django REST Framework + SimpleJWT |
| Frontend | Django Templates + Bootstrap 5 |
| Database | SQLite (dev) / PostgreSQL (production) |
| Search | PostgreSQL full-text (later) |
| Background tasks | Celery + Redis |
| Video courses | External hosting (YouTube/Vimeo URLs) |
| Payments | Razorpay (mock in dev if no keys) |
| Deployment | VPS / Cloud |

---

## Project structure

```
fintechaccountant/
├── config/                  # settings, urls, celery, views
├── apps/                    # 17 Django apps
│   ├── accounts/            # User, Role, auth, directory      (Phase 1)
│   ├── profiles/            # Profile, education, experience    (Phase 1)
│   ├── networking/          # Posts, feed, connections          (Phase 2)
│   ├── communities/         # Groups, topics, replies            (Phase 2)
│   ├── messaging/           # Threads, messages                  (Phase 2)
│   ├── events/              # Webinars, registrations            (Phase 2)
│   ├── courses/             # Catalog, modules, lessons, enroll   (Phase 3)
│   ├── instructors/         # Instructor profiles, payouts       (Phase 3)
│   ├── assessments/         # Quizzes, questions, attempts        (Phase 3)
│   ├── certificates/        # Course-completion certificates    (Phase 3)
│   ├── payments/            # Razorpay orders, subscriptions    (Phase 3)
│   ├── careers/             # Jobs, categories, alerts            (Phase 4)
│   ├── employers/           # Company profiles, interviews       (Phase 4)
│   ├── applications/        # Apply, track, shortlist            (Phase 4)
│   ├── notifications/       # In-app + announcements            (Shared)
│   ├── moderation/          # Reports, queue, actions            (Phase 5)
│   └── analytics/           # Dashboards, AI recommendation stubs (Phase 5)
├── templates/               # 82 Bootstrap templates
├── static/css/              # Brand stylesheet
├── scripts/                 # seed.py, template generators
├── manage.py
└── requirements.txt
```

Every app ships with: models, admin, forms, views, URLs, DRF serializers, DRF
viewsets and `api_urls.py`.

---

## Development roadmap (delivered)

- **Phase 1 — Foundation** — registration/login (email-based), multi-role
  User model, professional profiles with education/experience/skills/
  certifications/portfolio, professional directory, admin panel.
- **Phase 2 — Professional Network** — news feed with posts/articles/
  questions/images, comments, likes, follow + connect requests, communities
  with topics and replies, direct messaging (threads), events with
  registrations and speakers.
- **Phase 3 — Learning Platform** — course catalog with the 8 spec
  categories (Accounting, Taxation, Software, Finance, FinTech, Technology,
  Capital Markets, Professional Skills), modules & lessons, enrollment,
  progress tracking, instructor profiles, assessments (quizzes/exams/
  assignments) with auto-grading, course-completion certificates with
  public verification, paid courses via Razorpay checkout.
- **Phase 4 — Career Platform** — job board with the 12 spec career
  categories, employer company profiles, applications with status tracking,
  shortlisting, interview scheduling, candidate search, job alerts,
  credential verification with applicant consent.
- **Phase 5 — Growth & Intelligence** — admin analytics dashboard,
  recommendation stubs (course and job) using content-based filtering,
  moderation queue with reports and actions, in-app notifications.

---

## Revenue model (implemented in payments app)

| Source | Code |
| --- | --- |
| Premium membership | ₹299/month (top of ₹99–299 range) |
| Paid courses | per-course price (₹499–4,999) |
| Instructor commission | default 75% instructor / 25% platform (spec 15–25%) |
| Featured job listings | ₹999+ one-off |
| Recruiter subscription | ₹2,999/month |
| Paid events | per-event price |
| Corporate training | custom |

Free membership is always available.

---

## REST API

Every app exposes a DRF endpoint under `/api/v1/`. JWT auth under `/api/auth/`.

```
GET  /api/v1/accounts/users/?q=&role=
POST /api/v1/accounts/users/
GET  /api/v1/profiles/profiles/<slug>/
GET  /api/v1/network/posts/?feed=me
POST /api/v1/network/posts/<id>/like/
GET  /api/v1/courses/courses/
POST /api/v1/courses/courses/<slug>/enroll/
POST /api/v1/careers/jobs/
GET  /api/v1/applications/applications/
POST /api/v1/payments/orders/
POST /api/v1/payments/orders/<id>/verify/
POST /api/v1/certificates/certificates/verify/
GET  /api/v1/analytics/recommendations/
```

Browse interactively at `/api-auth/` (login required).

---

## Payments (Razorpay)

Without `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` set, the platform runs in
**mock mode**: the checkout page accepts any test payment id and completes
the order. Configure real keys in `.env` for production.

The payments app fulfils orders: paid course enrollments are activated,
event registrations recorded, premium memberships and recruiter
subscriptions started, featured job listings flagged.

---

## Certificates — important policy

Per spec, certificates issued by this platform are **course-completion
certificates only** and explicitly disclaim being CA, CMA, CS, CPA or any
other statutory qualification. The disclaimer is printed on every certificate
and returned by the API. Statutory qualifications are tracked separately on
the user profile via `profiles.Certification` with `is_statutory=True`.

Public verification at `/certificates/verify/` matches `certificate_id` +
`verification_code`.

---

## User roles

A single user can hold multiple roles simultaneously (learner, instructor
and employer). Roles: student, fresher, professional, accountant, CA, CMA,
CS, banker, instructor, institute, employer, admin.

---

## Running Celery (optional for dev)

```bash
# Terminal 1 - worker
celery -A config worker -l info
# Terminal 2 - beat (if scheduled tasks are added)
celery -A config beat -l info
```

A `redis` server must be running on `localhost:6379` (or set
`CELERY_BROKER_URL`).

---

## Testing

Smoke test verified (all return 200):
- Home, login, signup, directory, certificate verify
- List pages: `/courses/`, `/careers/`, `/communities/`, `/events/`,
  `/instructors/`, `/employers/`, `/accounts/directory/`
- Detail pages: course, job, event, instructor, employer, community
- API: `/api/v1/courses/courses/`, `/api/v1/careers/jobs/`,
  `/api/v1/communities/communities/`, `/api/v1/accounts/users/`
- Admin at `/admin/`
- Migrations apply cleanly to SQLite
- Seed data loads: 12 roles, 7 demo users, 2 instructors, 2 employers,
  8 course categories, **12 courses with 24 modules and 69 lessons**,
  12 job categories, 12 jobs, 10 communities, 4 upcoming events, 15 skills

---

## Production setup

### Database (PostgreSQL)

The default dev database is SQLite (zero-config). For production, install
PostgreSQL and set `DATABASE_URL` in `.env`:

```bash
# .env
DATABASE_URL=postgres://fintech:password@localhost:5432/fintechaccountant
```

`psycopg2-binary` and `dj-database-url` are in `requirements.txt`. Once the URL
is set, the settings file automatically switches the database engine.

### PDF certificates (WeasyPrint)

Course-completion certificates are rendered as real A4-landscape PDFs using
WeasyPrint (`apps/certificates/pdf.py`). When a user downloads their
certificate from `/certificates/my/`, a styled PDF is generated on demand and
cached on the `Certificate.pdf` field for subsequent downloads. If WeasyPrint
is unavailable, the view falls back to a printable HTML page.

### Razorpay (real payments)

Without `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` in `.env`, the platform runs
in **mock mode**: the checkout accepts any test payment id and fulfils the
order. Set real keys for production. The `razorpay` Python package is optional
— if absent, a mock client is used.

```bash
# .env
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
```

### AI recommendations

The recommenders in `apps/analytics/recommenders.py` use weighted content-based
filtering (skill overlap, keyword match, level match, location match,
popularity bonus) — not a trained ML model. The dashboard surface and the
`/api/v1/analytics/recommendations/` endpoint are in place; upgrading to an
embedding-based model only requires swapping that one file.

## Notes

- Video lessons store an external URL (YouTube/Vimeo) per the architecture
  spec — no on-platform video hosting.
- Celery is configured but optional for dev; email notifications, job-alert
  digests and video-transcoding hooks live there in production.

---

## License

Proprietary. © FinTech Accountant.
