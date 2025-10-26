from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.user import UserDB, UserLogin, UserCreate
from app.settings import settings
import logging

logger = logging.getLogger(__name__)

# Используем sha256_crypt вместо bcrypt для избежания проблем
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    logger.info(f"Hashing password of length: {len(password)}")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    logger.info(f"Authenticating user: {email}")
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        logger.warning(f"User not found: {email}")
        return False
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Invalid password for user: {email}")
        return False
    logger.info(f"User authenticated successfully: {email}")
    return user


def create_user(db: Session, user: UserCreate):
    logger.info(f"Creating user: {user.email}")
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created successfully: {user.email}")
    return db_user