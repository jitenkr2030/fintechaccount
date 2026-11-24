"""Heuristic AI recommendation engine (Phase 5).

Content-based filtering with weighted multi-factor scoring. Designed as a
drop-in replacement target for a future embedding/ML model — the dashboard
surface is already in place, only this file changes when upgrading.

Scoring factors:
  Courses:
    + skill overlap (0..0.5)
    + keyword match in headline/bio (0..0.2)
    + level match with user's experience (0..0.15)
    + popularity bonus (0..0.1)
    + featured bonus (0..0.05)
  Jobs:
    + skill overlap (0..0.5)
    + keyword match (0..0.15)
    + location match (0..0.15)
    + experience level match (0..0.1)
    + remote/WFH bonus (0..0.1)
"""
from django.db.models import Q

from .models import Recommendation


# ---- helpers ----
def _user_skills(user):
    """Return the user's skill names as a lowercased set."""
    from apps.profiles.models import ProfileSkill
    return {s.lower() for s in ProfileSkill.objects.filter(
        profile__user=user).values_list('skill__name', flat=True)}


def _user_keywords(user):
    """Headline + bio + current title as lowercased token set."""
    from apps.profiles.models import Profile
    text = ' '.join(filter(None, [
        user.headline, user.bio,
        getattr(getattr(user, 'profile', None), 'current_title', ''),
    ]))
    return {t for t in text.lower().split() if len(t) > 2}


def _skill_overlap(skills, text):
    """Count of user skills appearing in ``text``."""
    return sum(1 for s in skills if s in text)


def _experience_level(user):
    """Map user's years_experience to the job experience_level vocabulary."""
    from apps.profiles.models import Profile
    profile = getattr(user, 'profile', None)
    if not profile:
        return 'entry'
    yrs = profile.years_experience or 0
    if yrs <= 2:
        return 'entry'
    if yrs <= 7:
        return 'mid'
    if yrs <= 15:
        return 'senior'
    return 'leadership'


# ---- courses ----
def recommend_courses(user, limit=5):
    """Suggest courses based on skills, profile keywords, level and popularity."""
    from apps.courses.models import Course
    skills = _user_skills(user)
    keywords = _user_keywords(user)
    user_level = _experience_level(user)
    level_map = {'entry': Course.BEGINNER, 'mid': Course.INTERMEDIATE,
                  'senior': Course.ADVANCED, 'leadership': Course.ADVANCED}

    qs = (Course.objects.filter(status=Course.PUBLISHED)
          .exclude(enrollments__student=user)
          .select_related('category', 'instructor'))
    scored = []
    for c in qs:
        text = ' '.join(filter(None, [c.title, c.subtitle, c.description])).lower()
        # 1. Skill overlap (up to 0.5)
        overlap = _skill_overlap(skills, text)
        score = min(overlap * 0.15, 0.5)
        reason_parts = []
        if overlap:
            reason_parts.append(f'{overlap} skill match')
        # 2. Keyword match (up to 0.2)
        kw_hits = sum(1 for k in keywords if k in text)
        score += min(kw_hits * 0.04, 0.2)
        # 3. Level match (0.15)
        if c.level == level_map.get(user_level):
            score += 0.15
            reason_parts.append('matches your level')
        # 4. Popularity bonus (up to 0.1)
        if c.students_count:
            score += min(c.students_count / 5000.0, 0.1)
        # 5. Featured bonus (0.05)
        if c.is_featured:
            score += 0.05
        # Free bonus (small)
        if c.is_free:
            score += 0.02
        score = round(min(score, 1.0), 3)
        reason = ' · '.join(reason_parts) if reason_parts else 'Popular this week'
        scored.append((c, score, reason))

    scored.sort(key=lambda x: -x[1])
    recs = []
    for course, score, reason in scored[:limit]:
        if score <= 0:
            break
        rec, _ = Recommendation.objects.update_or_create(
            user=user, source=Recommendation.LEARNING, target_type='course',
            target_id=course.id,
            defaults={'target_text': course.title,
                      'target_url': f'/courses/{course.slug}/',
                      'reason': reason, 'score': score},
        )
        recs.append(rec)
    return recs


# ---- jobs ----
def recommend_jobs(user, limit=5):
    """Suggest open jobs matching the user's skills, location and experience."""
    from apps.careers.models import Job
    from apps.applications.models import JobApplication
    from apps.profiles.models import Profile

    skills = _user_skills(user)
    keywords = _user_keywords(user)
    user_level = _experience_level(user)
    profile = getattr(user, 'profile', None)
    user_city = (profile.current_company and '') or (user.city or '').lower()

    applied_ids = set(JobApplication.objects.filter(
        applicant=user).values_list('job_id', flat=True))
    qs = (Job.objects.filter(status=Job.OPEN)
          .exclude(id__in=applied_ids)
          .select_related('employer', 'category'))
    scored = []
    for j in qs:
        req = ' '.join(filter(None, [
            j.skills_required, j.title, j.description, j.requirements
        ])).lower()
        # 1. Skill overlap (up to 0.5)
        overlap = _skill_overlap(skills, req)
        score = min(overlap * 0.17, 0.5)
        reason_parts = []
        if overlap:
            reason_parts.append(f'{overlap} skill match')
        # 2. Keyword match (up to 0.15)
        kw_hits = sum(1 for k in keywords if k in req)
        score += min(kw_hits * 0.05, 0.15)
        # 3. Location match (up to 0.15)
        if user_city and j.location_city and user_city in j.location_city.lower():
            score += 0.15
            reason_parts.append('in your city')
        elif j.is_remote:
            score += 0.10
            reason_parts.append('remote')
        elif j.is_wfh:
            score += 0.07
        # 4. Experience level match (0.1)
        if j.experience_level == user_level:
            score += 0.10
            reason_parts.append('matches your experience')
        # 5. Featured bonus (small)
        if j.is_featured:
            score += 0.03
        score = round(min(score, 1.0), 3)
        reason = ' · '.join(reason_parts) if reason_parts else 'New opportunity'
        scored.append((j, score, reason))

    scored.sort(key=lambda x: -x[1])
    recs = []
    for job, score, reason in scored[:limit]:
        if score <= 0:
            break
        rec, _ = Recommendation.objects.update_or_create(
            user=user, source=Recommendation.CAREER, target_type='job',
            target_id=job.id,
            defaults={'target_text': job.title,
                      'target_url': f'/careers/{job.slug}/',
                      'reason': reason, 'score': score},
        )
        recs.append(rec)
    return recs
