from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
import os
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    first_name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    id_number = Column(String(50), nullable=True)
    department = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    two_factor_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    waste_entries = relationship('WasteEntry', back_populates='user')

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

class WasteEntry(Base):
    __tablename__ = 'waste_entries'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    department = Column(String(100), nullable=False)
    waste_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='waste_entries')

class JobTitle(Base):
    __tablename__ = 'job_titles'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TwoFactorAuth(Base):
    __tablename__ = 'two_factor_auth'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    secret_key = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PasswordReset(Base):
    __tablename__ = 'password_resets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
def init_db():
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://gmhlanga:2001@localhost:5432/waste_management'))
    Base.metadata.create_all(engine)
    return engine

engine = init_db()
Session = scoped_session(sessionmaker(bind=engine))

def get_session():
    return Session()