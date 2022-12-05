from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker


DATABASE_URI = "sqlite:///fedora-review-service.sqlite"
engine = create_engine(DATABASE_URI, echo=True)
session = sessionmaker(bind=engine)()
Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    topic = Column(String)
    done = Column(Boolean, default=False)
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
