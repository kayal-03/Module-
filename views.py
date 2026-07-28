from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AdminProfile, AssignmentScore, Attendance, Faculty, Marks, PerformancePrediction, Student
from .serializers import (
    AdminProfileSerializer, AssignmentScoreSerializer, AttendanceSerializer, FacultySerializer,
    MarksSerializer, PerformancePredictionSerializer, StudentSerializer,
)


def _create_prediction(student):
    return PerformancePrediction.objects.create(
        student=student,
        score=student.performance_score,
        status=student.performance_status,
        suggestion=student.improvement_suggestion,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def dashboard(request):
    students = Student.objects.all()
    summary = students.aggregate(total_students=Count("id"), average_score=Coalesce(Avg("internal_marks"), 0.0))
    return Response({
        "total_students": summary["total_students"],
        "average_internal_mark": round(summary["average_score"], 2),
        "performing_well": sum(student.performance_status == PerformancePrediction.WELL for student in students),
        "average": sum(student.performance_status == PerformancePrediction.AVERAGE for student in students),
        "at_risk": sum(student.performance_status == PerformancePrediction.AT_RISK for student in students),
        "recent_predictions": PerformancePredictionSerializer(PerformancePrediction.objects.all()[:5], many=True).data,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    required = ("username", "password", "name", "register_no", "department")
    missing = [field for field in required if not request.data.get(field)]
    if missing:
        return Response({"detail": f"Missing required fields: {', '.join(missing)}."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=request.data["username"]).exists():
        return Response({"username": ["This username is already in use."]}, status=status.HTTP_400_BAD_REQUEST)
    serializer = StudentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = User.objects.create_user(
        username=request.data["username"], password=request.data["password"], email=request.data.get("email", "")
    )
    student = serializer.save(user=user)
    token = RefreshToken.for_user(user)
    return Response({"student": StudentSerializer(student).data, "refresh": str(token), "access": str(token.access_token)}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
    if user is None:
        return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
    token = RefreshToken.for_user(user)
    profile = getattr(user, "student_profile", None)
    return Response({"access": str(token.access_token), "refresh": str(token), "user": {"id": user.id, "username": user.username}, "student": StudentSerializer(profile).data if profile else None})


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


class StudentViewSet(BaseViewSet):
    queryset = Student.objects.select_related("user").all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def predict(self, request, pk=None):
        student = self.get_object()
        prediction = _create_prediction(student)
        return Response(PerformancePredictionSerializer(prediction).data, status=status.HTTP_201_CREATED)


class FacultyViewSet(BaseViewSet):
    queryset = Faculty.objects.select_related("user").all()
    serializer_class = FacultySerializer


class AdminProfileViewSet(BaseViewSet):
    queryset = AdminProfile.objects.select_related("user").all()
    serializer_class = AdminProfileSerializer


class MarksViewSet(BaseViewSet):
    queryset = Marks.objects.select_related("student").all()
    serializer_class = MarksSerializer


class AttendanceViewSet(BaseViewSet):
    queryset = Attendance.objects.select_related("student").all()
    serializer_class = AttendanceSerializer


class AssignmentScoreViewSet(BaseViewSet):
    queryset = AssignmentScore.objects.select_related("student").all()
    serializer_class = AssignmentScoreSerializer


class PerformancePredictionViewSet(BaseViewSet):
    queryset = PerformancePrediction.objects.select_related("student").all()
    serializer_class = PerformancePredictionSerializer
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        student = get_object_or_404(Student, pk=request.data.get("student"))
        if not request.user.is_staff and student.user_id != request.user.id:
            return Response({"detail": "You can only predict your own performance."}, status=status.HTTP_403_FORBIDDEN)
        prediction = _create_prediction(student)
        return Response(self.get_serializer(prediction).data, status=status.HTTP_201_CREATED)
