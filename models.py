from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Student(models.Model):
    name = models.CharField(max_length=100)
    register_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    year = models.PositiveSmallIntegerField(default=1)
    attendance = models.FloatField(default=0)
    internal_marks = models.FloatField(default=0)
    assignment_marks = models.FloatField(default=0)
    test_marks = models.FloatField(default=0)
    study_hours_per_week = models.FloatField(default=0)
    user = models.OneToOneField(
        User,
        
        on_delete=models.SET_NULL, 
        related_name="student_profile",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["register_no"]

    def __str__(self):
        return f"{self.name} ({self.register_no})"

    @property
    def performance_score(self):
        return round(
            (self.attendance * 0.25)
            + (self.internal_marks * 0.25)
            + (self.assignment_marks * 0.20)
            + (self.test_marks * 0.25)
            + (min(self.study_hours_per_week, 20) / 20 * 100 * 0.05),
            2,
        )

    @property
    def performance_status(self):
        score = self.performance_score
        if score >= 75:
            return "well"
        if score >= 50:
            return "average"
        return "at_risk"

    @property
    def improvement_suggestion(self):
        suggestions = []
        if self.attendance < 75:
            suggestions.append("Improve attendance to at least 75%.")
        if self.internal_marks < 50:
            suggestions.append("Revise internal exam topics and request faculty feedback.")
        if self.assignment_marks < 50:
            suggestions.append("Submit assignments on time and improve assignment quality.")
        if self.test_marks < 50:
            suggestions.append("Practice previous test questions and attend remedial sessions.")
        if self.study_hours_per_week < 8:
            suggestions.append("Increase weekly study activity to 8 or more hours.")
        return " ".join(suggestions) or "Maintain the current learning routine."


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="faculty_profile",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Faculty"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.subject}"


class AdminProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default="Admin")
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="admin_profile",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="subject_marks")
    subject = models.CharField(max_length=100)
    score = models.FloatField()
    max_score = models.FloatField(default=100)
    exam_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Marks"
        ordering = ["student", "subject"]

    def __str__(self):
        return f"{self.student.name} - {self.subject}: {self.score}/{self.max_score}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.CharField(max_length=100)
    total_classes = models.PositiveIntegerField(default=0)
    attended_classes = models.PositiveIntegerField(default=0)
    recorded_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-recorded_on"]

    def __str__(self):
        return f"{self.student.name} - {self.subject}"

    @property
    def percentage(self):
        if self.total_classes == 0:
            return 0
        return round((self.attended_classes / self.total_classes) * 100, 2)


class AssignmentScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assignment_scores")
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    score = models.FloatField()
    max_score = models.FloatField(default=100)
    submitted_on = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-submitted_on"]

    def __str__(self):
        return f"{self.student.name} - {self.title}"


class PerformancePrediction(models.Model):
    WELL = "well"
    AVERAGE = "average"
    AT_RISK = "at_risk"

    STATUS_CHOICES = [
        (WELL, "Performing Well"),
        (AVERAGE, "Average"),
        (AT_RISK, "At Risk"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="predictions")
    score = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    suggestion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.name} - {self.get_status_display()}"
