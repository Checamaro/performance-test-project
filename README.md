# Performance Test Project

Полнофункциональное микросервисное приложение для тестирования производительности с автоматизацией тестирования, мониторингом и нагрузочным тестированием.

## Архитектура

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │────│   Backend   │────│  PostgreSQL │
│   (React)   │    │  (FastAPI)  │    │             │
└──────┬──────┘    └──────┬──────┘    └─────────────┘
       │                  │
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│ Selenium    │    │   Kafka     │
│   Tests     │    │   Broker    │
└──────┬──────┘    └──────┬──────┘
       │                  │
       │                  │
┌──────▼──────┐    ┌──────▼──────┐
│  Allure     │    │ Monitoring  │
│  Reports    │    │  Consumer   │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └───────┐    ┌─────┘
               │    │
         ┌─────▼────▼────┐
         │  Prometheus   │◄───┐
         └───────┬───────┘    │
                 │            │
             ┌───▼───┐        │
             │Grafana│────────┘
             └───────┘
```

## 🛠️ Технологический стек

- **Backend**: FastAPI, Python 3.12, SQLAlchemy, Pydantic
- **Frontend**: React, Axios
- **База данных**: PostgreSQL
- **Брокер сообщений**: Apache Kafka
- **Тестирование**: pytest, Locust, Selenium, Allure Reports
- **Мониторинг**: Prometheus, Grafana, Node Exporter
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: Github Actions

## 🚀 Быстрый старт

### Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ свободной RAM

### Запуск проекта

1. **Клонируйте репозиторий**:

- git clone <repository-url>
- cd performance-test-project

2. **Запустите все сервисы**:

- docker-compose up -d

3. **В браузере**:
- Frontend: http://localhost
- API Documentation: http://localhost:8000/docs
- Locust: http://localhost:8089
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000 (admin/admin)

4. **Тестирование**:
API тесты: pytest + Allure отчеты
Нагрузочные тесты: Locust
E2E тесты: Selenium (в разработке)
Интеграционные тесты: Kafka + PostgreSQL

5. **Docker сервисы**:

| Сервис | Порт | Назначение |
|--------|------|------------|
| backend | 8000 | FastAPI приложение |
| frontend | 80 | React приложение |
| postgres | 5432 | База данных |
| kafka | 9092 | Брокер сообщений |
| zookeeper | 2181 | Координатор Kafka |
| locust | 8089 | Нагрузочное тестирование |
| prometheus | 9091 | Сбор метрик |
| grafana | 3000 | Визуализация метрик |
| node-exporter | 9100 | Системные метрики |

6. **Запуск тестов**:

- API:
./scripts/run_tests.sh

- PERFOMANCE:
  - Откройте http://localhost:8089
  - Укажите количество пользователей и spawn rate
  - Запустите тест и наблюдайте за метриками

7. **Отчеты**:

- docker-compose run --rm tests allure open /tmp/allure-report

8. **Разработка**

    #### Backend
- cd backend
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- uvicorn main:app --reload

  #### Frontend
- cd frontend
- npm install
- npm start

9. **Проблемы с портами**
Если порт занят, измените его в docker-compose.yml

## 📊 Test Reports

### Latest Allure Report
[![Allure Report](https://img.shields.io/badge/Allure_Report-View_Online-green.svg)](https://checamaro.github.io/performance-test-project/)

### GitHub Actions
[![Tests](https://github.com/Checamaro/performance-test-project/actions/workflows/tests.yml/badge.svg)](https://github.com/Checamaro/performance-test-project/actions)
