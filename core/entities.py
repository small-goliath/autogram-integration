from sqlalchemy import Column, Integer, String, Text, DateTime, func, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

class InstagramSession(Base):
    __tablename__ = "instagram_sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    session_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class InstagramGroup(Base):
    __tablename__ = "instagram_group"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True, nullable=False)

class Consumer(Base):
    __tablename__ = "consumer"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)
    enabled = Column(Integer, default=0, nullable=False)
    group_id = Column(Integer, nullable=False)

class Producer(Base):
    __tablename__ = "producer"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)
    enabled = Column(Integer, default=0, nullable=False)
    group_id = Column(Integer, nullable=False)

class SnsRaiseUser(Base):
    __tablename__ = "sns_raise_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)

class UserActionVerification(Base):
    __tablename__ = "user_action_verification"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), nullable=False)
    link = Column(String(255), nullable=False)

class Checker(Base):
    __tablename__ = 'checker'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    session = Column(Text, nullable=False)

class UnfollowerCheck(Base):
    __tablename__ = "unfollower_checks"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), index=True, nullable=False)
    status = Column(String, default="idle")
    message = Column(String, nullable=True)
    _unfollowers = Column('unfollowers', Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    @property
    def unfollowers(self):
        if self._unfollowers is None:
            return None
        return json.loads(self._unfollowers)

    @unfollowers.setter
    def unfollowers(self, value):
        self._unfollowers = json.dumps(value) if value is not None else None

class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)
    ap_key = Column(String(32), nullable=False)

class RequestByWeek(Base):
    __tablename__ = 'request_by_week'
    username = Column(String(32), primary_key=True)
    link = Column(String(255), primary_key=True)
