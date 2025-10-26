from locust import HttpUser, task, between, TaskSet
import random
import json


class AuthBehavior(TaskSet):

    def on_start(self):
        """Called when a user starts executing this TaskSet"""
        self.user_id = None
        self.token = None
        self.email = f"loadtest_{random.randint(1000, 9999)}@example.com"
        self.password = "loadtestpassword123"

    @task(3)
    def register_user(self):
        """Test user registration under load"""
        response = self.client.post(
            "/register",
            json={"email": self.email, "password": self.password}
        )

        if response.status_code == 200:
            self.user_id = response.json().get("id")

    @task(5)
    def login_user(self):
        """Test user login under load"""
        response = self.client.post(
            "/login",
            data={"username": self.email, "password": self.password}
        )

        if response.status_code == 200:
            self.token = response.json().get("access_token")

    @task(2)
    def access_protected_endpoint(self):
        """Test accessing protected endpoint"""
        if self.token:
            self.client.get(
                "/users/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )


class WebsiteUser(HttpUser):
    tasks = [AuthBehavior]
    wait_time = between(1, 3)
    host = "http://backend:8000"