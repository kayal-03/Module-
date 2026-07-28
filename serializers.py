from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    AdminProfile,
    AssignmentScore,
    Attendance,
    Faculty,
    Marks,
    PerformancePrediction,
    Student,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
        read_only_fields = ("id",)


class StudentSerializer(serializers.ModelSerializer):
    performance_score = serializers.FloatField(read_only=True)
    performance_status = serializers.CharField(read_only=True)
    improvement_suggestion = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = (
            "id", "name", "register_no", "department", "email", "phone", "year",
            "attendance", "internal_marks", "assignment_marks", "test_marks",
            "study_hours_per_week", "user", "performance_score", "performance_status",
            "improvement_suggestion",
        )
        read_only_fields = ("id", "user", "performance_score", "performance_status", "improvement_suggestion")

    def validate(self, attrs):
        for field in ("attendance", "internal_marks", "assignment_marks", "test_marks"):
            value = attrs.get(field)
            if value is not None and not 0 <= value <= 100:
                raise serializers.ValidationError({field: "Enter a value from 0 to 100."})
        if attrs.get("study_hours_per_week", 0) < 0:
            raise serializers.ValidationError({"study_hours_per_week": "Study hours cannot be negative."})
        return attrs


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ("id", "name", "email", "department", "subject", "user")
        read_only_fields = ("id", "user")


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = ("id", "name", "email", "role", "user")
        read_only_fields = ("id", "user")


class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = ("id", "student", "subject", "score", "max_score", "exam_date")
        read_only_fields = ("id",)

    def validate(self, attrs):
        score = attrs.get("score", getattr(self.instance, "score", None))
        max_score = attrs.get("max_score", getattr(self.instance, "max_score", 100))
        if score is not None and (score < 0 or score > max_score):
            raise serializers.ValidationError({"score": "Score must be between 0 and max_score."})
        return attrs


class AttendanceSerializer(serializers.ModelSerializer):
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Attendance
        fields = ("id", "student", "subject", "total_classes", "attended_classes", "recorded_on", "percentage")
        read_only_fields = ("id", "percentage")

    def validate(self, attrs):
        attended = attrs.get("attended_classes", getattr(self.instance, "attended_classes", 0))
        total = attrs.get("total_classes", getattr(self.instance, "total_classes", 0))
        if attended > total:
            raise serializers.ValidationError({"attended_classes": "Attended classes cannot exceed total classes."})
        return attrs


class AssignmentScoreSerializer(MarksSerializer):
    class Meta:
        model = AssignmentScore
        fields = ("id", "student", "subject", "title", "score", "max_score", "submitted_on")
        read_only_fields = ("id",)


class PerformancePredictionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PerformancePrediction
        fields = ("id", "student", "score", "status", "status_display", "suggestion", "created_at")
        read_only_fields = ("id", "score", "status", "suggestion", "created_at")
