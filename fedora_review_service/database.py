import enum
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Enum,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship, backref
from fedora_review_service.config import config


engine = create_engine(config["database_uri"], echo=True)
session = sessionmaker(bind=engine)()
Base = declarative_base()


class Status(enum.Enum):
    ok = 1
    copr_build_failed = 2
    review_failed = 3


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True)
    topic = Column(String)
    done = Column(Boolean, default=False)
    created_on = Column(DateTime(timezone=True), server_default=func.now())


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    rhbz_id = Column(Integer, unique=True, nullable=False)
    owner = Column(String)
    created_on = Column(DateTime(timezone=True), server_default=func.now())


class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True)

    bugzilla_message_id = Column(Integer, ForeignKey("messages.id"))
    bugzilla_message = relationship(
        "Message", foreign_keys=[bugzilla_message_id])

    copr_message_id = Column(Integer, ForeignKey("messages.id"))
    copr_message = relationship("Message", foreign_keys=[copr_message_id])

    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    ticket = relationship("Ticket", backref=backref("builds"))

    spec_url = Column(String)
    srpm_url = Column(String)
    copr_build_id = Column(Integer)
    status = Column(Enum(Status))

    # A JSON list of issue names, e.g.
    # ["CheckLicensInDoc", "CheckNoNameConflict"]
    issues = Column(String)

    created_on = Column(DateTime(timezone=True), server_default=func.now())


def create_db():
    Base.metadata.create_all(engine)


def save_message(message):
    session.add(Message(id=message.id, topic=message.topic))
    session.commit()


def mark_done(message):
    obj = session.query(Message).get(message.id)
    obj.done = True
    session.add(obj)
    session.commit()
