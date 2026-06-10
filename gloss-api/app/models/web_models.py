from pydantic import BaseModel
from typing import Any, Optional, List


class MyResponse(BaseModel):
    status: str
    message: str = None
    data: Any = None

class PdfRequest(BaseModel):
    uuid: int
    file_name: str


class LinkRequest(BaseModel):
    uuid: Optional[int] = None
    link_name: str

class ParagraphRequest(BaseModel):
    uuid: int
    chat_id: int
    paragraph_number: int
    question: str
    source_text: str

class Option(BaseModel):
    uuid: int
    chat_id: int
    temperature: float
    need_table: bool
    past_questions: List[str]
    past_answers: List[str]
    paragraph_number: int
    source_text: str


class ChatRequest(BaseModel):
    question: str
    options: Option