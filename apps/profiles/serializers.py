"""DRF serializers for the profiles app."""
from rest_framework import serializers

from .models import (
    Skill, Profile, Education, Experience, Certification,
    ProfileSkill, PortfolioItem,
)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']


class ProfileSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = ProfileSkill
        fields = ['id', 'skill', 'skill_name', 'level']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'field_of_study',
                  'start_year', 'end_year', 'grade', 'description']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'title', 'company', 'employment_type', 'location',
                  'is_current', 'start_date', 'end_date', 'description']


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'issuing_body', 'is_statutory',
                  'issue_date', 'expiry_date', 'credential_id',
                  'credential_url', 'is_verified']


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id', 'title', 'item_type', 'description', 'url',
                  'image', 'completed_at']


class ProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_headline = serializers.CharField(source='user.headline', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    completion_pct = serializers.IntegerField(read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    skills = ProfileSkillSerializer(many=True, read_only=True)
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'user_email', 'user_name', 'user_headline', 'user_avatar',
            'slug', 'years_experience', 'current_title', 'current_company',
            'industry', 'website', 'linkedin', 'twitter', 'github',
            'is_open_to_work', 'is_open_to_mentor', 'is_open_to_speaking',
            'is_verified_professional', 'completion_pct',
            'followers_count', 'following_count', 'posts_count',
            'educations', 'experiences', 'certifications', 'skills',
            'portfolio_items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'slug', 'is_verified_professional', 'followers_count',
            'following_count', 'posts_count', 'created_at', 'updated_at',
        ]
