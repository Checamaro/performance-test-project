#!/usr/bin/env python3
"""
Упрощенный нагрузочный тест для CI
"""
import requests
import time
import random
import sys


def test_single_registration():
    """Тестируем одну регистрацию"""
    try:
        email = f'test_{random.randint(10000, 99999)}@example.com'
        print(f"Testing registration for: {email}")

        response = requests.post(
            'http://backend:8000/register',
            json={'email': email, 'password': 'testpassword123'},
            timeout=10
        )

        print(f"Status: {response.status_code}, Response: {response.text[:100]}")
        return response.status_code

    except Exception as e:
        print(f"Error: {e}")
        return None


def run_load_test():
    """Запускаем упрощенный нагрузочный тест"""
    print("Starting simplified load test...")

    # Сначала тестируем одиночный запрос
    print("1. Testing single request...")
    single_result = test_single_registration()

    if single_result != 200:
        print(f"❌ Single request failed: {single_result}")
        return False

    print("✅ Single request successful")

    # Затем запускаем несколько последовательных запросов
    print("2. Testing sequential requests...")
    successes = 0
    total_requests = 10

    start_time = time.time()

    for i in range(total_requests):
        result = test_single_registration()
        if result == 200:
            successes += 1
        else:
            print(f"Request {i + 1} failed: {result}")

        # Небольшая задержка между запросами
        time.sleep(0.3)

    duration = time.time() - start_time

    print(f"\n=== RESULTS ===")
    print(f"Successful: {successes}/{total_requests}")
    print(f"Duration: {duration:.2f}s")
    print(f"RPS: {total_requests / duration:.2f}")

    # Требуем 70% успешных запросов
    if successes >= 7:
        print("✅ Load test PASSED")
        return True
    else:
        print("❌ Load test FAILED")
        return False


if __name__ == "__main__":
    success = run_load_test()
    sys.exit(0 if success else 1)
