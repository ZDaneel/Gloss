import re
import traceback
from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.web_models import MyResponse, ParagraphRequest
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import chat_schemas
from app.db.crud import chat_crud

router = APIRouter()

ANNOTATION_PROMPT = """You are a close-reading assistant. Your task is to annotate a source text with citation markers based on a reader's question.

Instructions:
1. Read the source text and the question carefully.
2. Insert citation markers [1], [2], [3], etc. DIRECTLY INTO the source text at the exact spots most relevant to the question. Place each marker immediately after the relevant phrase or at the end of the relevant sentence.
3. Keep every word of the source text VERBATIM — do not change, summarize, or rearrange anything.
4. Number markers sequentially [1], [2], [3], ... in the order they appear in the text (top to bottom).
5. Mark only 2–5 of the most relevant passages. Do not over-annotate.
6. Return ONLY the annotated source text. No preamble, no explanation, no answer to the question."""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _split_into_cited_paragraphs(annotated_text: str) -> list[str]:
    """Split annotated text into paragraphs; keep only those containing [n] markers."""
    # Try double-newline split first
    chunks = [p.strip() for p in re.split(r'\n{2,}', annotated_text.strip()) if p.strip()]
    # Fall back to single-newline if text has no blank lines
    if len(chunks) < 2:
        chunks = [p.strip() for p in annotated_text.strip().splitlines() if p.strip()]
    cited = [p for p in chunks if re.search(r'\[\d+\]', p)]
    return cited if cited else chunks


@router.post("/", response_model=MyResponse, response_model_exclude_unset=True)
async def get_paragraphs(
    paragraph_request: ParagraphRequest, db: Session = Depends(get_db)
):
    print(f"[paragraphs] uuid={paragraph_request.uuid} question={paragraph_request.question[:50]!r}")

    source_text = paragraph_request.source_text
    print(f"[paragraphs] source_text length={len(source_text)}")

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        messages = [
            {"role": "system", "content": ANNOTATION_PROMPT},
            {
                "role": "user",
                "content": f"Source text:\n{source_text}\n\nQuestion: {paragraph_request.question}",
            },
        ]
        print("[paragraphs] calling OpenAI for annotation...")
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.1,
            stream=False,
            timeout=settings.chat_timeout,
        )
        annotated_text = response.choices[0].message.content or ""
        print(f"[paragraphs] annotated text length={len(annotated_text)}")
        print(f"[paragraphs] === ANNOTATED TEXT ===\n{annotated_text}\n=== END ===")
    except Exception as e:
        print(f"[paragraphs] OpenAI error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {e}")

    paragraphs = _split_into_cited_paragraphs(annotated_text)
    print(f"[paragraphs] split into {len(paragraphs)} cited paragraphs")

    title_raw = source_text.strip()
    paper_title = (title_raw[:60] + "...") if len(title_raw) > 60 else title_raw

    try:
        with db.begin():
            db_history = chat_crud.get_history(db, paragraph_request.uuid)
            if not db_history:
                chat_crud.create_history(
                    db, chat_schemas.HistoryCreate(id=paragraph_request.uuid)
                )
                print("[paragraphs] created new history")
            chat_crud.partial_update_history(
                db, chat_schemas.HistoryUpdate(id=paragraph_request.uuid, paper_title=paper_title)
            )
            chat_crud.create_chat(
                db,
                chat_schemas.ChatsCreate(
                    chat_id=paragraph_request.chat_id,
                    history_id=paragraph_request.uuid,
                    question=paragraph_request.question,
                    paragraphs=paragraphs,
                ),
            )
        db.commit()
        print("[paragraphs] DB write OK")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[paragraphs] DB error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")

    return MyResponse(
        status="Success",
        data={
            "paragraphs": paragraphs,
            "paperTitle": paper_title,
            "annotatedText": annotated_text,
        },
    )
