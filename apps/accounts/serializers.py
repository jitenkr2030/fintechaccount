"""DRF serializers for accounts."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'label', 'description']


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    display_role = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'headline', 'bio', 'avatar', 'avatar_url',
            'city', 'state', 'country',
            'is_email_verified', 'is_phone_verified', 'is_identity_verified',
            'is_premium', 'display_role', 'roles',
            'last_active', 'date_joined',
        ]
        read_only_fields = [
            'id', 'is_email_verified', 'is_phone_verified', 'is_identity_verified',
            'is_premium', 'last_active', 'date_joined',
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            url = obj.avatar.url
            return request.build_absolute_uri(url) if request else url
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    role_names = serializers.ListField(
        child=serializers.ChoiceField(choices=Role.ROLE_CHOICES),
        required=False, write_only=True,
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password',
                  'phone', 'headline', 'city', 'state', 'role_names']

    def create(self, validated_data):
        role_names = validated_data.pop('role_names', [])
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        for name in role_names:
            user.add_role(name)
        return user
