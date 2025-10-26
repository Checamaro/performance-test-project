from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Метрики для аутентификации
auth_requests_total = Counter(
    'auth_requests_total',
    'Total authentication requests',
    ['endpoint', 'method', 'status']
)

auth_request_duration = Histogram(
    'auth_request_duration_seconds',
    'Authentication request duration in seconds',
    ['endpoint', 'method']
)

active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

user_registrations = Counter(
    'user_registrations_total',
    'Total user registrations'
)

user_logins = Counter(
    'user_logins_total',
    'Total user logins',
    ['status']  # success or failure
)

kafka_events_sent = Counter(
    'kafka_events_sent_total',
    'Total Kafka events sent',
    ['event_type']
)

# Функция для получения метрик
def get_metrics():
    return generate_latest()