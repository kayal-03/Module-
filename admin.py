from django.contrib import admin

from .models import (
    AdminProfile,
    AssignmentScore,
    Attendance,
    Faculty,
    Marks,
    PerformancePrediction,
    Student,
)    


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "register_no",
        "name",
        "department",
        "year",
        "attendance",
        "performance_score",
        "performance_status",
    )
    search_fields = ("name", "register_no", "department")
    list_filter = ("department", "year")


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department", "subject")
    search_fields = ("name", "email", "subject")
    list_filter = ("department",)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "role")
    search_fields = ("name", "email")


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "score", "max_score", "exam_date")
    search_fields = ("student__name", "student__register_no", "subject")
    list_filter = ("subject", "exam_date")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "attended_classes", "total_classes", "percentage", "recorded_on")
    search_fields = ("student__name", "student__register_no", "subject")
    list_filter = ("subject", "recorded_on")


@admin.register(AssignmentScore)
class AssignmentScoreAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "title", "score", "max_score", "submitted_on")
    search_fields = ("student__name", "student__register_no", "subject", "title")
    list_filter = ("subject", "submitted_on")


@admin.register(PerformancePrediction)
class PerformancePredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "score", "status", "created_at")
    search_fields = ("student__name", "student__register_no", "status")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at",)
