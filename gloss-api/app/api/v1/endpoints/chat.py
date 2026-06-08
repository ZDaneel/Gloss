import json
import httpx
import asyncio
import time
from openai import AsyncOpenAI, OpenAI
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, List
from app.models.web_models import ChatRequest, Option
from pydantic import BaseModel
from app.core.config import settings
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.models import chat_schemas
from app.db.crud import chat_crud
from app.models.web_models import MyResponse

API_KEY = ""
API_URL = "https://api.openai.com/v1/chat/completions"
API_HEADERS = {"Authorization": f"Bearer {API_KEY}"}
API_MODEL = "gpt-4o-mini"

asyncClient = AsyncOpenAI(api_key=API_KEY)
client = OpenAI(api_key=API_KEY)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def event_stream_generator0(message: str) -> AsyncGenerator[str, None]:
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                API_URL,
                headers=API_HEADERS,
                json={
                    "model": API_MODEL,
                    "messages": [{"role": "user", "content": message}],
                    "stream": True,
                },
            ) as response:
                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    while "data: " in buffer:
                        split_index = buffer.find("data: ")
                        if split_index == -1:
                            break

                        data_chunk = buffer[split_index:].split("\n", 1)[0]
                        buffer = buffer[split_index + len(data_chunk) + 1 :]

                        if data_chunk.strip() == "data: [DONE]":
                            return

                        json_str = data_chunk[6:].strip()
                        try:
                            chunk_json = json.loads(json_str)
                            if "choices" in chunk_json and chunk_json["choices"][0].get(
                                "delta", {}
                            ).get("content"):
                                text_chunk = chunk_json["choices"][0]["delta"][
                                    "content"
                                ]
                                yield text_chunk
                        except json.JSONDecodeError:
                            continue
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail=f"HTTP error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def event_stream_generator2(message: str) -> AsyncGenerator[str, None]:
    try:
        # text = "The data [1] used in the experiments include:\n1. **MMLU (Massive Multitask Language Understanding [2])**: This dataset [4] is not described in detail within the provided references, but it is implied to be a part of the experiments [3].\n2. **BBH (BIG-Bench Hard)**: Derived from a subset of tasks within the BIG-Bench benchmark, focusing on multiple-choice tasks where existing Large Language Models (LLMs) struggle to reach average human-rater performance. Demonstrations for each subset are provided in Chen et al. (2023) [5].hhhhhhh \\(\\{x^{i}_{t}\\}_{i=1}^{n}\\) hello \\[Input=\\{t(x^{1}_{s},y^{1}_{s}),...,t(x^{K}_{s},y^{K}_{s}),t(x^{i}_{t})\\}, \\tag{1}\\] \\[ E = mc^2, \\tag{1}\\] \\(\\alpha\\)"
        text = "The main method introduced in this paper is **Matryoshka Representation Learning (MRL)**. Key points about MRL from the provided references include:\n1. **Objective and Contribution**: MRL aims to create flexible representations that adapt to varying computational resources for multiple downstream tasks. It encodes information at different granularities, allowing a single embedding to adapt to the computational constraints of downstream tasks without additional cost during inference and deployment [1].\n2. **Implementation Details**: MRL optimizes the multi-class classification loss for each nested dimension using standard empirical risk minimization with a separate linear classifier for each dimension. \nIt aggregates all losses after scaling with their relative importance, optimizing for a set of nested dimensions to produce accurate representations that interpolate for dimensions between the chosen granularity [2].\n3. **Efficiency and Accuracy**: MRL improves efficiency for large-scale classification and retrieval tasks without significant loss of accuracy. It enables up to 14× smaller embedding size for ImageNet-1K classification at the same level of accuracy, up to 14× real-world speed-ups for large-scale retrieval on ImageNet-1K and 4K, and up to 2% accuracy improvements for long-tail few-shot classification [1][4]."
        for char in text:
            await asyncio.sleep(0.02)
            yield char
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-process")
async def chat_process(chat_request: ChatRequest, db: Session = Depends(get_db)):
    headers = {"Content-Type": "application/octet-stream"}
    accumulated_data: List[str] = []

    async def event_stream():
        try:
            async for text_chunk in event_stream_generator(chat_request):
                accumulated_data.append(text_chunk)
                yield text_chunk
        except asyncio.CancelledError:
            asyncio.create_task(
                handle_chat_update(
                    db, chat_request, "".join(accumulated_data), "cancelled"
                )
            )
            raise
        except Exception as e:
            asyncio.create_task(
                handle_chat_update(db, chat_request, "".join(accumulated_data), str(e))
            )
            raise HTTPException(status_code=500, detail=str(e))
        else:
            asyncio.create_task(
                handle_chat_update(db, chat_request, "".join(accumulated_data))
            )

    return StreamingResponse(event_stream(), headers=headers)


async def handle_chat_update(
    db: Session, chat_request: ChatRequest, accumulated_data_str: str, error=None
):
    try:
        chat = chat_schemas.ChatsUpdate(
            chat_id=chat_request.options.chat_id,
            history_id=chat_request.options.uuid,
            content=accumulated_data_str,
            temperature=chat_request.options.temperature,
            need_table=chat_request.options.need_table,
            past_questions=chat_request.options.past_questions,
            past_answers=chat_request.options.past_answers,
            error_message=error,
        )
        await asyncio.to_thread(chat_crud.update_chat, db, chat)
        await asyncio.to_thread(db.commit)
    except Exception as e:
        print(f"Error updating chat: {e}")


async def event_stream_generator(
    chat_request: ChatRequest,
) -> AsyncGenerator[str, None]:
    API_URL = settings.mock_url + "/v1/chat/completions"
    API_HEADERS = {"Content-Type": "application/json"}
    timeout = httpx.Timeout(settings.chat_timeout)
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                API_URL,
                headers=API_HEADERS,
                json=chat_request.model_dump(),
                timeout=timeout,
            ) as response:
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to fetch data from external service",
                    )
                async for chunk in response.aiter_text():
                    yield chunk
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class LikeRequest(BaseModel):
    uuid: int
    chat_id: int
    is_good: bool


@router.post("/like")
async def like(link_request: LikeRequest, db: Session = Depends(get_db)):
    print(f"Like request: {link_request}")
    try:
        chat = chat_schemas.ChatsUpdateGood(
            chat_id=link_request.chat_id,
            history_id=link_request.uuid,
            is_good=link_request.is_good,
        )
        await asyncio.to_thread(chat_crud.update_chat_good, db, chat)
        await asyncio.to_thread(db.commit)
    except Exception as e:
        print(f"Error updating chat: {e}")
    return MyResponse(status="Success")
