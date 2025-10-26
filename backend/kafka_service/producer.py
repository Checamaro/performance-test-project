from kafka import KafkaProducer
import json
import logging
from app.settings import settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    def __init__(self):
        self.producer = None
        self.topic = settings.kafka_auth_topic

    def connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                request_timeout_ms=10000,
                api_version_auto_timeout_ms=30000
            )
            logger.info(f"Connected to Kafka successfully at {settings.kafka_bootstrap_servers}")
            # Тестируем подключение
            future = self.producer.send(self.topic, {'test': 'connection'})
            future.get(timeout=10)
            logger.info("Kafka connection test successful")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.producer = None

    def send_auth_event(self, event_type: str, user_data: dict):
        if not self.producer:
            logger.info("Connecting to Kafka...")
            self.connect()
            if not self.producer:
                logger.error("Kafka producer not available")
                return

        event = {
            "event_type": event_type,
            "user_data": user_data,
            "timestamp": str(__import__('datetime').datetime.utcnow())
        }

        try:
            future = self.producer.send(self.topic, event)
            future.get(timeout=10)  # Ждем подтверждения
            logger.info(f"Successfully sent auth event: {event_type} for user {user_data.get('email')}")
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}")


# Глобальный инстанс продюсера
auth_producer = KafkaEventProducer()