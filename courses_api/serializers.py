# serializers.py
from rest_framework import serializers
from .models import User, Course, Lesson, Enrollment, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for custom User model"""

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "password_hash",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""

    class Meta:
        model = Course
        fields = [
            "id",
            "instructor",
            "title",
            "slug",
            "description",
            "status",
            "price_usd",
            "language",
            "thumbnail_url",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "position",
            "title",
            "content_url",
            "content_type",
            "duration_sec",
            "free_preview",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "course",
            "status",
            "enrolled_at",
            "last_accessed_at",
            "progress_pct",
        ]
        read_only_fields = ["id", "enrolled_at"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""

    class Meta:
        model = Comment
        fields = [
            "id",
            "course",
            "user",
            "parent_comment",
            "body",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
