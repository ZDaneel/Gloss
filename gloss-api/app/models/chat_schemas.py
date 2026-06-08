from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from datetime import datetime
import pytz


class HistoryBase(BaseModel):
    id: int


class HistoryCreate(HistoryBase):
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))


class HistoryUpdate(HistoryBase):
    paper_title: str


class History(HistoryBase):
    paper_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResourcesBase(BaseModel):
    history_id: int
    is_file: bool
    resource_name: str


class ResourcesCreate(ResourcesBase):
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))


class Resources(ResourcesBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatsBase(BaseModel):
    chat_id: int
    history_id: int


class ChatsCreate(ChatsBase):
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))
    question: str
    paragraphs: List[str]


class ChatsUpdate(ChatsBase):
    content: str
    temperature: float
    need_table: bool
    past_questions: List[str]
    past_answers: List[str]
    error_message: Optional[str] = None


class ChatsUpdateGood(ChatsBase):
    is_good: bool


class Chats(ChatsBase):
    id: int
    content: Optional[str]
    temperature: float
    need_table: float
    paragraphs: List[str]
    past_questions: Optional[List[str]]
    past_answers: Optional[List[str]]
    error_message: Optional[str]
    is_good: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True
