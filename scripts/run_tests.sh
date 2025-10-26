#!/bin/bash

echo "Starting test environment..."
docker-compose up -d backend postgres kafka

echo "Waiting for services to be ready (60 seconds)..."
sleep 60

echo "Checking backend health..."
curl -f http://localhost:8000/health || echo "Backend not ready yet, waiting..."
sleep 10

echo "Running API tests..."
docker-compose run --rm tests python -m pytest api/ -v --alluredir=/tmp/allure-results

echo "Generating Allure report..."
docker-compose run --rm tests allure generate /tmp/allure-results -o /tmp/allure-report --clean

echo "Tests completed!"
echo "To view Allure report: docker-compose run --rm tests allure open /tmp/allure-report"
echo "To run load tests: http://localhost:8089"