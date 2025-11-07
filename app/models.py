from sqlalchemy import Column, Integer, String, Text , Date, Time
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    chunk_strategy = Column(String, nullable=False)
    content = Column(Text, nullable=False)

class InterviewBooking_table(Base):
    __tablename__ = "interview_bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)