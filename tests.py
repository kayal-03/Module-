from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Student


class StudentApiTests(APITestCase):
    def test_registration_login_and_prediction(self):
        payload = {
            "username": "kajal",
            "password": "StrongPass123!",
            "name": "Kajal Varshini",
            "register_no": "CS001",
            "department": "Computer Science",
            "attendance": 85,
            "internal_marks": 78,
            "assignment_marks": 82,
            "test_marks": 80,
            "study_hours_per_week": 10,
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("access", response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        prediction = self.client.post(f"/api/students/{response.data['student']['id']}/predict/", format="json")
        self.assertEqual(prediction.status_code, 201)
        self.assertEqual(prediction.data["status"], "well")

        login = self.client.post("/api/login/", {"username": "kajal", "password": "StrongPass123!"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertIn("refresh", login.data)

    def test_student_cannot_view_another_students_profile(self):
        first_user = User.objects.create_user(username="first", password="StrongPass123!")
        second_user = User.objects.create_user(username="second", password="StrongPass123!")
        Student.objects.create(name="First", register_no="CS002", department="CS", user=first_user)
        Student.objects.create(name="Second", register_no="CS003", department="CS", user=second_user)

        login = self.client.post("/api/login/", {"username": "first", "password": "StrongPass123!"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.get("/api/students/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["register_no"], "CS002")
