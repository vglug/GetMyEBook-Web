from sqlalchemy import Column, Integer, String
import uuid as uuid_module
from .base import Base

from .. import logger


log = logger.create()

class Library_Id(Base):
    __tablename__ = 'library_id'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, default=lambda: str(uuid_module.uuid4()))


def init_library_id(session):
    try:
        library_id_count = session.query(Library_Id).count()
        if library_id_count == 0:
            lib_id = Library_Id(id=1)
            session.add(lib_id)
            session.commit()
            log.info("Default library_id record created successfully.")
    except Exception as e:
        session.rollback()
        log.warning(f"Could not create default library_id record: {e}")
