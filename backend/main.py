from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database.database import get_db, engine
from models.user import Base, UserDB, UserCreate, UserResponse, Token
from services.auth import authenticate_user, create_user, create_access_token, verify_password, get_password_hash
from kafka_service.producer import auth_producer
from app.settings import settings
from monitoring.metrics import (
    auth_requests_total, auth_request_duration, active_users,
    user_registrations, user_logins, kafka_events_sent, get_metrics
)

# Создаем таблицы с обработкой ошибок и принудительно
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    # Проверяем что таблицы создались
    with engine.connect() as conn:
        result = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in result]
        logger.info(f"Available tables: {tables}")

except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Не падаем, возможно таблицы уже созданы

app = FastAPI(title="Auth Service", version="1.0.0")


# Middleware для сбора метрик
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Собираем метрики
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    auth_requests_total.labels(
        endpoint=endpoint,
        method=method,
        status=status_code
    ).inc()

    auth_request_duration.labels(
        endpoint=endpoint,
        method=method
    ).observe(process_time)

    return response


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Подключаемся к Kafka при старте
@app.on_event("startup")
async def startup_event():
    auth_producer.connect()

    # Дополнительная проверка таблиц при старте
    try:
        with engine.connect() as conn:
            # Простая проверка - пытаемся выбрать из таблицы
            conn.execute("SELECT 1 FROM users LIMIT 1")
            logger.info("Users table exists and accessible")

            # Устанавливаем начальное значение активных пользователей
            result = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = true")
            active_users.set(result.scalar())
    except Exception as e:
        logger.warning(f"Users table check failed: {e}, attempting to create tables...")
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created on startup")
        except Exception as create_error:
            logger.error(f"Failed to create tables: {create_error}")


@app.get("/")
async def root():
    return {"message": "Auth Service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Эндпоинт для Prometheus метрик
@app.get("/metrics")
async def metrics():
    return Response(get_metrics(), media_type="text/plain")


@app.post("/register-simple")
async def register_simple(user_data: dict):
    """
    Упрощенный эндпоинт для регистрации для нагрузочного тестирования
    Без Kafka и сложных зависимостей
    """
    try:
        email = user_data.get("email")
        password = user_data.get("password")

        if not email or not password:
            return {"error": "Email and password required"}, 400

        # Простая проверка - всегда возвращаем успех для тестирования
        return {
            "message": "User registered successfully",
            "email": email,
            "status": "active"
        }

    except Exception as e:
        logger.error(f"Simple registration error: {e}")
        return {"error": "Registration failed"}, 500


@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Проверяем, существует ли пользователь
        db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Создаем пользователя
        hashed_password = get_password_hash(user.password)
        db_user = UserDB(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Обновляем метрики
        user_registrations.inc()
        active_users.inc()

        # Отправляем событие в Kafka
        auth_producer.send_auth_event("user_registered", {
            "user_id": db_user.id,
            "email": db_user.email
        })
        kafka_events_sent.labels(event_type="user_registered").inc()

        return db_user

    except Exception as e:
        logger.error(f"Error in register: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Обновляем метрики для неудачного логина
        user_logins.labels(status="failure").inc()

        # Отправляем событие в Kafka
        auth_producer.send_auth_event("login_failed", {
            "email": form_data.username,
            "reason": "invalid_credentials"
        })
        kafka_events_sent.labels(event_type="login_failed").inc()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Обновляем время последнего входа
    user.last_login = datetime.utcnow()
    db.commit()

    # Обновляем метрики для успешного логина
    user_logins.labels(status="success").inc()

    # Создаем токен
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Отправляем событие в Kafka
    auth_producer.send_auth_event("login_success", {
        "user_id": user.id,
        "email": user.email
    })
    kafka_events_sent.labels(event_type="login_success").inc()

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user is None:
        raise credentials_exception
    return user