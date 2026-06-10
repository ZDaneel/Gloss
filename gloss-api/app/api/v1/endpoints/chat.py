import asyncio
from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, List
from pydantic import BaseModel
from app.core.config import settings
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.models import chat_schemas
from app.db.crud import chat_crud
from app.models.web_models import ChatRequest, MyResponse

CITATION_PROMPT = """You are a close-reading assistant for humanities and social science texts (psychology, philosophy, sociology, etc.).

The source text has already been annotated with citation markers [1] [2] [3] at the most relevant passages.

Rules:
1. Answer ONLY based on the provided source text — do not introduce outside knowledge.
2. Reuse the pre-existing [n] marker numbers when you cite a passage — do NOT invent new numbers or renumber.
3. Weave the citation markers inline naturally throughout your answer (e.g. "The author argues [1] that...").
4. Do NOT add a reference list at the end — inline markers only.
5. CRITICAL — Language: Respond in the SAME language as the user's question. English question → English answer. Chinese question → Chinese answer."""

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def _openai_stream(
    question: str,
    source_text: str,
    past_questions: List[str],
    past_answers: List[str],
    temperature: float,
) -> AsyncGenerator[str, None]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    messages = [{"role": "system", "content": CITATION_PROMPT}]
    for q, a in zip(past_questions, past_answers):
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({
        "role": "user",
        "content": f"原文：\n{source_text}\n\n问题：{question}",
    })
    stream = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=temperature,
        stream=True,
        timeout=settings.chat_timeout,
    )
    async for chunk in stream:
        yield chunk.choices[0].delta.content or ""


@router.post("/chat-process")
async def chat_process(chat_request: ChatRequest, db: Session = Depends(get_db)):
    source_text = chat_request.options.source_text
    print(f"[chat] === SOURCE TEXT (annotated) ===\n{source_text}\n=== END ===")

    accumulated: List[str] = []

    async def event_stream():
        try:
            async for chunk in _openai_stream(
                chat_request.question,
                source_text,
                chat_request.options.past_questions,
                chat_request.options.past_answers,
                chat_request.options.temperature,
            ):
                accumulated.append(chunk)
                yield chunk
        except asyncio.CancelledError:
            asyncio.create_task(
                _save_chat(db, chat_request, "".join(accumulated), "cancelled")
            )
            raise
        except Exception as e:
            asyncio.create_task(
                _save_chat(db, chat_request, "".join(accumulated), str(e))
            )
            raise HTTPException(status_code=500, detail=str(e))
        else:
            asyncio.create_task(_save_chat(db, chat_request, "".join(accumulated)))

    return StreamingResponse(event_stream(), headers={"Content-Type": "application/octet-stream"})


async def _save_chat(
    db: Session, chat_request: ChatRequest, content: str, error: str = None
):
    try:
        chat = chat_schemas.ChatsUpdate(
            chat_id=chat_request.options.chat_id,
            history_id=chat_request.options.uuid,
            content=content,
            temperature=chat_request.options.temperature,
            need_table=chat_request.options.need_table,
            past_questions=chat_request.options.past_questions,
            past_answers=chat_request.options.past_answers,
            error_message=error,
        )
        await asyncio.to_thread(chat_crud.update_chat, db, chat)
        await asyncio.to_thread(db.commit)
    except Exception as e:
        print(f"Error saving chat: {e}")


class LikeRequest(BaseModel):
    uuid: int
    chat_id: int
    is_good: bool


@router.post("/like")
async def like(like_request: LikeRequest, db: Session = Depends(get_db)):
    try:
        chat = chat_schemas.ChatsUpdateGood(
            chat_id=like_request.chat_id,
            history_id=like_request.uuid,
            is_good=like_request.is_good,
        )
        await asyncio.to_thread(chat_crud.update_chat_good, db, chat)
        await asyncio.to_thread(db.commit)
    except Exception as e:
        print(f"Error updating like: {e}")
    return MyResponse(status="Success")
