#!/bin/bash

set -e

echo "Starting CI test environment..."

# Запускаем сервисы
docker-compose up -d backend postgres kafka

echo "Waiting for services to be ready..."
# Ждем пока бэкенд станет доступен
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "Backend is ready!"
        break
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 2
done

# Проверяем здоровье бэкенда
curl -f http://localhost:8000/health || {
    echo "Backend health check failed"
    docker-compose logs backend
    exit 1
}

echo "Running API tests..."
docker-compose run --rm tests python -m pytest api/ -v --alluredir=/tmp/allure-results

echo "Generating Allure report..."
docker-compose run --rm tests allure generate /tmp/allure-results -o allure-report --clean

echo "Tests completed successfully!"

# Сохраняем логи для отладки
docker-compose logs backend > backend.logs
docker-compose logs postgres > postgres.logs

echo "Backend logs saved to backend.logs"
echo "Allure report generated in allure-report/"