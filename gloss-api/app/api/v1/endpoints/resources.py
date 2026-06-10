from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import chat_schemas
from app.db.crud import chat_crud
from app.db.session import SessionLocal
from app.models.web_models import MyResponse
from app.utils.source import options as id_options, generator

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TextRequest(BaseModel):
    content: str


@router.post("/upload-text/", response_model=MyResponse, response_model_exclude_unset=True)
async def upload_text(request: TextRequest, db: Session = Depends(get_db)):
    my_uuid = _generate_uuid()
    try:
        with db.begin():
            history = chat_schemas.HistoryCreate(id=my_uuid)
            chat_crud.create_history(db, history)
            resource = chat_schemas.ResourcesCreate(
                history_id=my_uuid, is_file=False, resource_name=request.content
            )
            chat_crud.create_resources(db, resource)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")
    return MyResponse(status="Success", message=str(my_uuid))


def _generate_uuid() -> int:
    opts = id_options.IdGeneratorOptions()
    idgen = generator.DefaultIdGenerator()
    idgen.set_id_generator(opts)
    return idgen.next_id()
