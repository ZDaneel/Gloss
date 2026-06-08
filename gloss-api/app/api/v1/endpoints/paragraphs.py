import httpx
from fastapi import APIRouter, HTTPException, Depends
from app.models.web_models import MyResponse, ParagraphRequest
from app.core.config import settings
from app.db.session import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import chat_schemas
from app.db.crud import chat_crud

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MyResponse, response_model_exclude_unset=True)
async def get_paragraphs(
    paragraph_request: ParagraphRequest, db: Session = Depends(get_db)
):
    timeout = httpx.Timeout(settings.paragraph_timeout)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.mock_url + "/paragraphs",
            json=paragraph_request.model_dump(),
            timeout=timeout,
        )
        if response.status_code == 200:
            response_data = response.json()
            try:
                with db.begin():
                    data = MyResponse(**response_data)
                    paragraphs = data.data.get("paragraphs")
                    paperTitle = data.data.get("paperTitle")
                    history = chat_schemas.HistoryUpdate(
                        id=paragraph_request.uuid, paper_title=paperTitle
                    )
                    chat_crud.partial_update_history(db, history)
                    chat_create = chat_schemas.ChatsCreate(
                        chat_id=paragraph_request.chat_id,
                        history_id=paragraph_request.uuid,
                        question=paragraph_request.question,
                        paragraphs=paragraphs,
                    )
                    chat_crud.create_chat(db, chat_create)
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Database operation failed: {e}"
                )
            return data
        else:
            return MyResponse(data={}, status="Error")
