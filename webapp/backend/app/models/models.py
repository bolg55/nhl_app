from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    team = Column(String)
    raw_position = Column(String)
    stats = relationship("PlayerStats", back_populates="player")
    salaries = relationship("PlayerSalary", back_populates="player")
    injuries = relationship("PlayerInjury", back_populates="player")

    __table_args__ = (
        UniqueConstraint('name', 'team', 'position', name='unique_player_identifier'),
    )

class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    date = Column(Date)
    toi = Column(Float)
    goals_per_60 = Column(Float)
    assists_per_60 = Column(Float)
    shots_per_60 = Column(Float)
    ixg_per_60 = Column(Float)

    player = relationship("Player", back_populates="stats")

class PlayerSalary(Base):
    __tablename__ = "player_salaries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    salary = Column(Float)  # in millions
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="salaries")

class PlayerInjury(Base):
    __tablename__ = "player_injuries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    status = Column(String)  # e.g., "IR", "DTD", etc.
    description = Column(String, nullable=True)
    expected_return = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    player = relationship("Player", back_populates="injuries")

class TeamStandings(Base):
    __tablename__ = "team_standings"

    id = Column(Integer, primary_key=True, index=True)
    team = Column(String, unique=True)
    points_percentage = Column(Float)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LeagueSettings(Base):
    __tablename__ = "league_settings"

    id = Column(Integer, primary_key=True, index=True)
    max_salary_cap = Column(Float)
    min_salary_cap_pct = Column(Float, default=0.99)
    num_forwards = Column(Integer)
    num_defense = Column(Integer)
    num_goalies = Column(Integer)
    max_players_per_team = Column(Integer, default=5)
    max_defense_per_team = Column(Integer, default=1)
    points_goal = Column(Float)
    points_assist = Column(Float)
    points_goalie_win = Column(Float)