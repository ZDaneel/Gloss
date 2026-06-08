import os
import re
import httpx
import asyncio
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models import chat_schemas
from app.db.crud import chat_crud
from app.db.session import SessionLocal

from app.core.config import settings
from app.models.web_models import MyResponse, PdfRequest, LinkRequest
from app.utils.source import options as id_options, generator

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/upload-pdf/", response_model=MyResponse, response_model_exclude_unset=True
)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await handle_pdf_upload(file, db)


@router.post(
    "/upload-pdf/{uuid}", response_model=MyResponse, response_model_exclude_unset=True
)
async def upload_pdf_with_uuid(
    uuid: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    return await handle_pdf_upload(file, db, uuid)


@router.post(
    "/upload-link/", response_model=MyResponse, response_model_exclude_unset=True
)
async def upload_link(link_request: LinkRequest, db: Session = Depends(get_db)):
    return await handle_link_upload(link_request.link_name, db)


@router.post(
    "/upload-link/{uuid}", response_model=MyResponse, response_model_exclude_unset=True
)
async def upload_link_with_uuid(
    uuid: int, link_request: LinkRequest, db: Session = Depends(get_db)
):
    return await handle_link_upload(link_request.link_name, db, uuid)


@router.post(
    "/remove-pdf", response_model=MyResponse, response_model_exclude_unset=True
)
async def remove_pdf(params: PdfRequest, db: Session = Depends(get_db)):
    uuid = params.uuid
    file_name = params.file_name
    try:
        resources = chat_crud.get_resources_by_history_id_and_name(db, uuid, file_name)
        if resources is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        if chat_crud.delete_resources(db, resources.id):
            db.commit()
        else:
            raise HTTPException(status_code=500, detail="Resource deletion failed")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")

    file_location = os.path.join(settings.upload_dir, str(uuid), file_name)
    if os.path.exists(file_location):
        os.remove(file_location)
    return MyResponse(status="Success", message="File removed successfully")


@router.post(
    "/remove-link", response_model=MyResponse, response_model_exclude_unset=True
)
async def remove_link(params: LinkRequest, db: Session = Depends(get_db)):
    uuid = params.uuid
    link_name = params.link_name
    try:
        resources = chat_crud.get_resources_by_history_id_and_name(db, uuid, link_name)
        if resources is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        if chat_crud.delete_resources(db, resources.id):
            db.commit()
        else:
            raise HTTPException(status_code=500, detail="Resource deletion failed")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")

    return MyResponse(status="Success", message="Link removed successfully")


async def async_upload_pdf_to_model(uuid: int, content: bytes, filename: str):
    API_URL = settings.mock_url + "/upload-pdf/" + str(uuid)
    async with httpx.AsyncClient() as client:
        await client.post(
            API_URL,
            files={"file": (filename, content, "application/pdf")},
        )


async def handle_pdf_upload(file: UploadFile, db: Session, uuid: int = None):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF files are allowed."
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="File size exceeds the maximum limit of 10 MB."
        )

    my_uuid = generate_uuid(uuid)

    unique_folder = f"{my_uuid}"
    file_location = os.path.join(settings.upload_dir, unique_folder, file.filename)

    try:
        await save_file(content, file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File saving failed: {e}")

    isFirst = uuid is None
    try:
        create_history_and_resources(db, my_uuid, True, file.filename, isFirst)
    except SQLAlchemyError as e:
        handle_database_exception(e, file_location)

    try:
        asyncio.create_task(async_upload_pdf_to_model(my_uuid, content, file.filename))
    except Exception as e:
        print(f"Error: {e}")

    return MyResponse(status="Success", message=str(my_uuid))


def add_https_prefix(link: str) -> str:
    if not link.startswith(("http://", "https://")):
        return "https://" + link
    return link


async def check_link_accessibility(link: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(link)
            return response.status_code == 200
    except httpx.RequestError:
        return False


async def async_upload_link_to_model(uuid: str, link_name: str):
    API_URL = settings.mock_url + "/upload-link"
    API_HEADERS = {"Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        await client.post(
            API_URL,
            headers=API_HEADERS,
            json=LinkRequest(uuid=uuid, link_name=link_name).model_dump(),
        )


async def handle_link_upload(link_name: str, db: Session, uuid: int = None):
    pattern = re.compile(
        r"([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})",
        re.IGNORECASE,
    )
    if not pattern.match(link_name):
        return MyResponse(status="Error", message="linkWrong")

    link_name_with_prefix = add_https_prefix(link_name)
    if not await check_link_accessibility(link_name_with_prefix):
        if link_name_with_prefix.startswith("https://"):
            link_name_with_prefix = "http://" + link_name_with_prefix[8:]
            if not await check_link_accessibility(link_name_with_prefix):
                return MyResponse(status="Error", message="linkUnavailable")
        else:
            return MyResponse(status="Error", message="linkUnavailable")

    my_uuid = generate_uuid(uuid)

    isFirst = uuid is None

    try:
        create_history_and_resources(db, my_uuid, False, link_name, isFirst)
    except SQLAlchemyError as e:
        handle_database_exception(e)

    try:
        asyncio.create_task(async_upload_link_to_model(my_uuid, link_name))
    except Exception as e:
        print(f"Error: {e}")

    return MyResponse(status="Success", message=str(my_uuid))


def generate_uuid(uuid: int = None) -> int:
    if uuid is not None:
        return uuid
    options = id_options.IdGeneratorOptions()
    idgen = generator.DefaultIdGenerator()
    idgen.set_id_generator(options)
    return idgen.next_id()


def create_history_and_resources(
    db: Session, uuid: int, is_file: bool, resource_name: str, isFirst: bool = True
):
    with db.begin():
        if isFirst:
            history = chat_schemas.HistoryCreate(id=uuid)
            chat_crud.create_history(db, history)

        resources = chat_schemas.ResourcesCreate(
            history_id=uuid, is_file=is_file, resource_name=resource_name
        )
        chat_crud.create_resources(db, resources)
    db.commit()


def handle_database_exception(e: SQLAlchemyError, file_location: str = None):

    if file_location and os.path.exists(file_location):
        os.remove(file_location)
    raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")


async def save_file(content: bytes, file_location: str):
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(content)
