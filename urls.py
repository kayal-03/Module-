from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register("students", views.StudentViewSet)
router.register("faculty", views.FacultyViewSet)
router.register("admins", views.AdminProfileViewSet)
router.register("marks", views.MarksViewSet)
router.register("attendance", views.AttendanceViewSet)
router.register("assignments", views.AssignmentScoreViewSet)
router.register("predictions", views.PerformancePredictionViewSet)

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/dashboard/", views.dashboard, name="api-dashboard"),
    path("api/register/", views.register, name="api-register"),
    path("api/login/", views.login, name="api-login"),
    path("api/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/", include(router.urls)),
]
