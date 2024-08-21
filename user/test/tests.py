from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class UserAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.signup_url = "/user/signup/"
        cls.login_url = "/user/signin/"
        cls.auth_user_url = "/user/signin/"

        # 테스트 사용자 생성
        cls.user = User.objects.create_user(email="testuser@example.com", password="testpass123")

    def test_user_signup(self):
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
        }
        response = self.client.post(self.signup_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["token"])
        self.assertIn("refresh", response.data["token"])

    def test_user_login(self):
        data = {"email": "testuser@example.com", "password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["token"])
        self.assertIn("refresh", response.data["token"])

    def test_auth_user(self):
        # JWT 토큰 생성
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(self.auth_user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_login_wrong_password(self):
        data = {"email": "testuser@example.com", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "비밀번호가 틀렸습니다.")

    def test_login_nonexistent_user(self):
        data = {"email": "nonexistent@example.com", "password": "doesntmatter"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "존재하지 않는 아이디입니다.")
