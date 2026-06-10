from sqlalchemy.orm import Session
from app.models import chat_schemas
from app.db.models import chat_models


def create_history(db: Session, history: chat_schemas.HistoryCreate):
    db_history = chat_models.History(id=history.id)
    db.add(db_history)
    db.flush()
    return db_history


def get_historys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(chat_models.History).offset(skip).limit(limit).all()


def get_history(db: Session, history_id: int):
    return (
        db.query(chat_models.History)
        .filter(chat_models.History.id == history_id)
        .first()
    )


def partial_update_history(db: Session, history: chat_schemas.HistoryUpdate):
    db_history = (
        db.query(chat_models.History)
        .filter(chat_models.History.id == history.id)
        .first()
    )
    if not db_history:
        return None
    for key, value in history.model_dump(exclude_unset=True).items():
        setattr(db_history, key, value)
    db.flush()
    return db_history


def create_resources(db: Session, resources: chat_schemas.ResourcesCreate):
    db_resources = chat_models.Resources(
        history_id=resources.history_id,
        is_file=resources.is_file,
        resource_name=resources.resource_name,
    )
    db.add(db_resources)
    db.flush()
    return db_resources


def get_resources_by_history_id_and_name(
    db: Session, history_id: int, resource_name: str
):
    return (
        db.query(chat_models.Resources)
        .filter(
            chat_models.Resources.history_id == history_id,
            chat_models.Resources.resource_name == resource_name,
        )
        .first()
    )


def get_resource_by_history_id(db: Session, history_id: int):
    return (
        db.query(chat_models.Resources)
        .filter(chat_models.Resources.history_id == history_id)
        .first()
    )


def delete_resources(db: Session, resources_id: int):
    db.query(chat_models.Resources).filter(
        chat_models.Resources.id == resources_id
    ).delete()
    db.commit()
    return True

def create_chat(db: Session, chat: chat_schemas.ChatsCreate):
    db_chat = chat_models.Chats(
        chat_id=chat.chat_id,
        history_id=chat.history_id,
        question=chat.question,
        paragraphs=chat.paragraphs,
    )
    db.add(db_chat)
    db.flush()
    return db_chat

def update_chat(db: Session, chat: chat_schemas.ChatsUpdate):
    db_chat = (
        db.query(chat_models.Chats)
        .filter(
            chat_models.Chats.chat_id == chat.chat_id,
            chat_models.Chats.history_id == chat.history_id,
        )
        .first()
    )
    if not db_chat:
        return None
    for key, value in chat.model_dump(exclude_unset=True).items():
        setattr(db_chat, key, value)
    db.flush()
    return 

def update_chat_good(db: Session, chat: chat_schemas.ChatsUpdateGood):
    db_chat = (
        db.query(chat_models.Chats)
        .filter(
            chat_models.Chats.chat_id == chat.chat_id,
            chat_models.Chats.history_id == chat.history_id,
        )
        .first()
    )
    if not db_chat:
        return None
    db_chat.is_good = chat.is_good
    db.flush()
    return db_chat
