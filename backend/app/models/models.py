from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from ..database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    team = Column(String)
    position = Column(String)
    stats = relationship("PlayerStats", back_populates="player")

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

class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    value = Column(Float)  # in millions
    date = Column(Date)  # to track salary changes over time

class LeagueSettings(Base):
    __tablename__ = "league_settings"

    id = Column(Integer, primary_key=True, index=True)
    max_salary_cap = Column(Float)
    num_forwards = Column(Integer)
    num_defense = Column(Integer)
    num_goalies = Column(Integer)
    points_goal = Column(Float)
    points_assist = Column(Float)
    points_goalie_win = Column(Float)