"""Custom User model for FinTech Accountant.

A single account holds one professional identity that can carry multiple roles
across the three ecosystems:
  - Student / Fresher / Professional / Accountant / CA / CMA / CS
  - Banking & Finance professional
  - Trainer / Instructor
  - College / Training Institute (organisation account)
  - Company / Recruiter (employer)
  - Platform Administrator

A single person can be a learner, an instructor and an employer at the same
time, so roles are stored as a many-to-many relationship to a Role model rather
than a single choice field.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
class Role(models.Model):
    """A user role that gates access to features across the platform.

    Roles defined in spec Section 3 (User types):
      student, fresher, professional, accountant, ca, cma, cs,
      banker, instructor, institute, employer, admin
    """

    STUDENT = 'student'
    FRESHER = 'fresher'
    PROFESSIONAL = 'professional'
    ACCOUNTANT = 'accountant'
    CA = 'ca'           # Chartered Accountant
    CMA = 'cma'          # Cost & Management Accountant
    CS = 'cs'            # Company Secretary
    BANKER = 'banker'    # Banking & Finance professional
    INSTRUCTOR = 'instructor'
    INSTITUTE = 'institute'
    EMPLOYER = 'employer'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (STUDENT, _('Student')),
        (FRESHER, _('Fresher')),
        (PROFESSIONAL, _('Working Professional')),
        (ACCOUNTANT, _('Accountant')),
        (CA, _('Chartered Accountant')),
        (CMA, _('CMA Professional')),
        (CS, _('Company Secretary')),
        (BANKER, _('Banking & Finance Professional')),
        (INSTRUCTOR, _('Trainer / Instructor')),
        (INSTITUTE, _('College / Training Institute')),
        (EMPLOYER, _('Company / Recruiter')),
        (ADMIN, _('Platform Administrator')),
    ]

    name = models.CharField(_('role name'), max_length=30, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.get_name_display()


# ---------------------------------------------------------------------------
# User Manager
# ---------------------------------------------------------------------------
class UserManager(BaseUserManager):
    """Custom manager that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('is_active', True)
        if extra.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        user = self._create_user(email, password, **extra)
        admin_role = Role.objects.filter(name=Role.ADMIN).first()
        if admin_role:
            user.roles.add(admin_role)
        return user


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(AbstractUser):
    """Platform user with one professional identity and multiple roles.

    Replaces username with email. A user can be a learner, an instructor and
    an employer at the same time, so the roles are many-to-many.
    """

    # Remove username, use email
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Identity
    first_name = models.CharField(_('first name'), max_length=80)
    last_name = models.CharField(_('last name'), max_length=80, blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    headline = models.CharField(_('headline'), max_length=200, blank=True,
                                help_text=_('e.g. "CA Finalist | GST Practitioner"'))
    bio = models.TextField(_('bio'), blank=True)

    # Location (India-first, international-ready)
    city = models.CharField(_('city'), max_length=80, blank=True)
    state = models.CharField(_('state'), max_length=80, blank=True)
    country = models.CharField(_('country'), max_length=80, default='India')

    # Verification
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_identity_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(_('premium member'), default=False)

    # Activity
    last_active = models.DateTimeField(default=timezone.now)

    # Roles
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        full = f'{self.first_name} {self.last_name}'.strip()
        return full

    def get_short_name(self):
        return self.first_name

    @property
    def display_role(self):
        """Primary role label for display."""
        first = self.roles.first()
        return first.get_name_display() if first else 'Member'

    # --- Role helpers (single person can have multiple roles) ---
    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    def add_role(self, role_name):
        role = Role.objects.filter(name=role_name).first()
        if role and not self.roles.filter(pk=role.pk).exists():
            self.roles.add(role)
            return True
        return False

    def remove_role(self, role_name):
        role = Role.objects.filter(name=role_name).first()
        if role:
            self.roles.remove(role)
            return True
        return False

    # --- Boolean role checks used by templates / permissions ---
    @property
    def is_student(self):
        return self.has_role(Role.STUDENT)

    @property
    def is_instructor(self):
        return self.has_role(Role.INSTRUCTOR)

    @property
    def is_employer(self):
        return self.has_role(Role.EMPLOYER)

    @property
    def is_institute(self):
        return self.has_role(Role.INSTITUTE)

    @property
    def is_admin_role(self):
        return self.has_role(Role.ADMIN) or self.is_superuser

    @property
    def is_professional(self):
        return self.has_role(Role.PROFESSIONAL) or self.has_role(Role.ACCOUNTANT) \
            or self.has_role(Role.CA) or self.has_role(Role.CMA) \
            or self.has_role(Role.CS) or self.has_role(Role.BANKER)
