from datetime import datetime, date
from sqlalchemy import (
    BigInteger, String, Integer, Boolean, DateTime, Date, 
    Text, Float, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    language: Mapped[str] = mapped_column(String(5), default="uz")
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(32), default="Beginner")
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    wrong_answers: Mapped[int] = mapped_column(Integer, default=0)
    battles_won: Mapped[int] = mapped_column(Integer, default=0)
    battles_lost: Mapped[int] = mapped_column(Integer, default=0)
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_daily: Mapped[date | None] = mapped_column(Date, nullable=True)
    favorite_club: Mapped[str | None] = mapped_column(String(64), nullable=True)
    best_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    quiz_sessions = relationship("QuizSession", back_populates="user")
    answered_questions = relationship("UserQuestionHistory", back_populates="user")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    difficulty: Mapped[str] = mapped_column(String(16), index=True)  # easy, medium, hard, expert
    question_uz: Mapped[str] = mapped_column(Text)
    question_en: Mapped[str] = mapped_column(Text)
    question_ru: Mapped[str] = mapped_column(Text)
    options_uz: Mapped[str] = mapped_column(Text)  # JSON list
    options_en: Mapped[str] = mapped_column(Text)
    options_ru: Mapped[str] = mapped_column(Text)
    correct_index: Mapped[int] = mapped_column(Integer)  # 0-3
    explanation_uz: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    times_shown: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserQuestionHistory(Base):
    __tablename__ = "user_question_history"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"), index=True)
    was_correct: Mapped[bool] = mapped_column(Boolean)
    answered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="answered_questions")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    mode: Mapped[str] = mapped_column(String(32))  # quiz, guess_player, guess_club, etc.
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(16), nullable=True)
    current_question: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=10)
    score: Mapped[int] = mapped_column(Integer, default=0)
    question_ids: Mapped[str] = mapped_column(Text, default="[]")  # JSON list of question ids
    answers: Mapped[str] = mapped_column(Text, default="[]")  # JSON list of user answers
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="quiz_sessions")


class Battle(Base):
    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    player2_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="waiting")  # waiting, active, finished
    question_ids: Mapped[str] = mapped_column(Text, default="[]")
    player1_score: Mapped[int] = mapped_column(Integer, default=0)
    player2_score: Mapped[int] = mapped_column(Integer, default=0)
    player1_answers: Mapped[str] = mapped_column(Text, default="[]")
    player2_answers: Mapped[str] = mapped_column(Text, default="[]")
    current_q: Mapped[int] = mapped_column(Integer, default=0)
    winner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    question_ids: Mapped[str] = mapped_column(Text)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserDailyProgress(Base):
    __tablename__ = "user_daily_progress"
    __table_args__ = (UniqueConstraint("user_id", "challenge_date", name="uq_user_daily"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    challenge_date: Mapped[date] = mapped_column(Date)
    score: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)