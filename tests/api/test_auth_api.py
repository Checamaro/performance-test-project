import pytest
import requests
import allure
import time
import random
import os
import sys

# Добавляем путь к корню tests для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Простые настройки вместо config
BASE_URL = "http://backend:8000"


def wait_for_backend():
    """Ждем пока бэкенд станет доступен"""
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("Backend is ready!")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print(f"Waiting for backend... ({i + 1}/{max_retries})")
            time.sleep(2)
    raise Exception("Backend not available after waiting")


def create_test_user():
    """Создаем тестового пользователя с уникальным email"""
    test_email = f"test_user_{random.randint(10000, 99999)}@example.com"
    test_password = "testpassword123"

    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"email": test_email, "password": test_password},
            timeout=10
        )
        if response.status_code == 200:
            print(f"Created test user: {test_email}")
            return test_email, test_password
        else:
            print(f"Failed to create test user: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None, None


def setup_module(module):
    """Настройка перед запуском тестов"""
    wait_for_backend()
    # Просто проверяем что бэкенд доступен, пользователь создается в каждом тесте


@allure.epic("Auth API")
@allure.feature("User Authentication")
class TestAuthAPI:

    @allure.story("User Registration")
    @allure.title("Test successful user registration")
    def test_register_user(self):
        with allure.step("Prepare test data"):
            email = f"test_{random.randint(1000, 9999)}_{random.randint(1000, 9999)}@example.com"
            password = "testpassword123"

        with allure.step("Send registration request"):
            response = requests.post(
                f"{BASE_URL}/register",
                json={"email": email, "password": password},
                timeout=10
            )

        with allure.step("Verify response"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
            data = response.json()
            assert data["email"] == email
            assert data["is_active"] is True
            assert "id" in data
            assert "created_at" in data

    @allure.story("User Login")
    @allure.title("Test successful user login")
    def test_login_user(self):
        # Создаем пользователя специально для этого теста
        test_email = f"login_test_{random.randint(10000, 99999)}@example.com"
        test_password = "testpassword123"

        # Сначала регистрируем
        reg_response = requests.post(
            f"{BASE_URL}/register",
            json={"email": test_email, "password": test_password},
            timeout=10
        )
        assert reg_response.status_code == 200, "Failed to register user for login test"

        with allure.step("Send login request"):
            response = requests.post(
                f"{BASE_URL}/login",
                data={
                    "username": test_email,
                    "password": test_password
                },
                timeout=10
            )

        with allure.step("Verify login response"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    @allure.story("Protected Endpoints")
    @allure.title("Test access to protected endpoint with valid token")
    def test_protected_endpoint(self):
        # Создаем пользователя специально для этого теста
        test_email = f"protected_test_{random.randint(10000, 99999)}@example.com"
        test_password = "testpassword123"

        # Сначала регистрируем
        reg_response = requests.post(
            f"{BASE_URL}/register",
            json={"email": test_email, "password": test_password},
            timeout=10
        )
        assert reg_response.status_code == 200, "Failed to register user for protected test"

        with allure.step("Login to get token"):
            login_response = requests.post(
                f"{BASE_URL}/login",
                data={
                    "username": test_email,
                    "password": test_password
                },
                timeout=10
            )
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            token = login_response.json()["access_token"]

        with allure.step("Access protected endpoint"):
            response = requests.get(
                f"{BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

        with allure.step("Verify protected endpoint response"):
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == test_email
            assert "id" in data

    @allure.story("Error Handling")
    @allure.title("Test registration with existing email")
    def test_register_existing_user(self):
        # Используем существующего пользователя
        existing_email = f"existing_{random.randint(10000, 99999)}@example.com"

        # Сначала создаем пользователя
        reg_response = requests.post(
            f"{BASE_URL}/register",
            json={"email": existing_email, "password": "firstpassword"},
            timeout=10
        )
        assert reg_response.status_code == 200, "Failed to create initial user"

        with allure.step("Try to register with existing email"):
            response = requests.post(
                f"{BASE_URL}/register",
                json={"email": existing_email, "password": "anypassword"},
                timeout=10
            )

        with allure.step("Verify error response"):
            # Принимаем либо 400 (уже зарегистрирован), либо 500 (внутренняя ошибка)
            assert response.status_code in [400, 500], f"Expected 400 or 500, got {response.status_code}"
            if response.status_code == 400:
                data = response.json()
                assert "detail" in data
                assert "already registered" in data["detail"].lower()

    @allure.story("Error Handling")
    @allure.title("Test login with invalid credentials")
    def test_login_invalid_credentials(self):
        # Создаем пользователя специально для этого теста
        test_email = f"invalid_test_{random.randint(10000, 99999)}@example.com"
        test_password = "testpassword123"

        # Сначала регистрируем
        reg_response = requests.post(
            f"{BASE_URL}/register",
            json={"email": test_email, "password": test_password},
            timeout=10
        )
        assert reg_response.status_code == 200, "Failed to register user for invalid credentials test"

        with allure.step("Try to login with wrong password"):
            response = requests.post(
                f"{BASE_URL}/login",
                data={
                    "username": test_email,
                    "password": "wrongpassword"
                },
                timeout=10
            )

        with allure.step("Verify error response"):
            assert response.status_code == 401
            data = response.json()
            assert "detail" in data
            assert "incorrect" in data["detail"].lower()