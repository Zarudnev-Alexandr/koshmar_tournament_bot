import enum
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, func, BigInteger, Integer, String, Float, Date, ForeignKey, Boolean, Text, Enum, Index, \
    JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class TournamentType(enum.Enum):
    CUSTOM = "Кастомки"
    TDM = "ТДМ турниры"
    METRO = "Метро турниры"


class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    fio: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    pubg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    ticket_balance: Mapped[int] = mapped_column(Integer, default=0)
    completed_mandatory_task = mapped_column(Boolean, default=False)
    invited_tg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'), nullable=True)

    invited_by: Mapped["User"] = relationship("User", remote_side=[tg_id])

    tournaments = relationship("TournamentParticipation", back_populates="user")
    organization = relationship("Organization", back_populates="user", uselist=False)


class Tournament(Base):
    __tablename__ = 'tournaments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[TournamentType] = mapped_column(Enum(TournamentType), index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price_in_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    total_slots: Mapped[int] = mapped_column(Integer, nullable=False)
    reward_first_place: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    group_link: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[str] = mapped_column(String, nullable=False)
    photo_url: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_started: Mapped[bool] = mapped_column(Boolean, default=False)

    participants = relationship("TournamentParticipation", back_populates="tournament")


class TournamentParticipation(Base):
    __tablename__ = 'tournament_participation'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    tournament_id: Mapped[int] = mapped_column(ForeignKey('tournaments.id'))
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tournaments")
    tournament = relationship("Tournament", back_populates="participants")


class Giveaway(Base):
    __tablename__ = 'giveaways'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sponsors: Mapped[list] = mapped_column(JSON)
    end_type: Mapped[str] = mapped_column(String)
    end_value: Mapped[int] = mapped_column(Integer)
    prize_places: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_rewards: Mapped[list] = mapped_column(JSON)
    photo_url: Mapped[str] = mapped_column(String, nullable=True)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)

    participants = relationship("GiveawayParticipation", back_populates="giveaway")


class GiveawayParticipation(Base):
    __tablename__ = 'giveaway_participation'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    giveaway_id: Mapped[int] = mapped_column(ForeignKey('giveaways.id'))
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="giveaway_participation")
    giveaway = relationship("Giveaway", back_populates="participants")


class TicketPurchase(Base):
    __tablename__ = 'ticket_purchases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_ticket: Mapped[float] = mapped_column(Float, nullable=False)  # фиксируем цену на момент покупки
    purchase_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="ticket_purchases")


class MandatoryTask(Base):
    __tablename__ = 'mandatory_tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)
    channel_link: Mapped[str] = mapped_column(String, nullable=False)
    channel_name: Mapped[str] = mapped_column(String, nullable=False)


class Organization(Base):
    __tablename__ = 'organizations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.tg_id'), unique=True)

    user = relationship("User", back_populates="organization")

