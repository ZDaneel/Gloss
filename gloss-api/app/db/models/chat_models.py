from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, Text, Boolean, ARRAY, Numeric
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime
import pytz


class History(Base):
    __tablename__ = "history"

    id = Column(BigInteger, primary_key=True, index=True)
    paper_title = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(pytz.UTC))

    resources = relationship("Resources", back_populates="history")
    chats = relationship("Chats", back_populates="history")


class Resources(Base):
    __tablename__ = "resources"

    id = Column(BigInteger, primary_key=True, index=True)
    history_id = Column(BigInteger, ForeignKey("history.id"), nullable=False)
    is_file = Column(Boolean, nullable=False)
    resource_name = Column(Text, index=True , nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(pytz.UTC))

    history = relationship("History", back_populates="resources")

class Chats(Base):
    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True, index=True)
    chat_id = Column(BigInteger, index=True, nullable=False)
    history_id = Column(BigInteger, ForeignKey("history.id"), nullable=False)
    question = Column(Text, nullable=False)
    content = Column(Text)
    paragraphs = Column(ARRAY(Text))
    temperature = Column(Numeric(10,2), nullable=False)
    need_table = Column(Boolean)
    past_questions = Column(ARRAY(Text))
    past_answers = Column(ARRAY(Text))
    error_message = Column(Text)
    is_good = Column(Boolean)
    created_at = Column(DateTime(timezone=True), default=datetime.now(pytz.UTC))

    history = relationship("History", back_populates="chats")