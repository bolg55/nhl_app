from pydantic import BaseModel
from datetime import date
from typing import List, Optional

class PlayerBase(BaseModel):
    name: str
    team: str
    position: str

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int

    class Config:
        from_attributes = True

class PlayerStatsBase(BaseModel):
    date: date
    toi: float
    goals_per_60: float
    assists_per_60: float
    shots_per_60: float
    ixg_per_60: float

class PlayerStatsCreate(PlayerStatsBase):
    player_id: int

class PlayerStats(PlayerStatsBase):
    id: int
    player_id: int

    class Config:
        from_attributes = True

class LeagueSettingsBase(BaseModel):
    # Salary constraints
    max_salary_cap: float
    min_salary_cap_pct: float = 0.99  # Default 99% of max

    # Roster requirements
    num_forwards: int
    num_defense: int
    num_goalies: int
    max_players_per_team: int = 5

    # Scoring settings
    points_goal: float
    points_assist: float
    points_goalie_win: float

    # Optional additional settings
    min_forwards_per_team: int = 0  # If you want to require min forwards from same team
    max_forwards_per_team: int = None  # If you want to limit forwards from same team
    max_defense_per_team: int = 1  # Your current 1 defenseman per team rule

class LeagueSettingsCreate(LeagueSettingsBase):
    pass

class LeagueSettings(LeagueSettingsBase):
    id: int

    class Config:
        from_attributes = True

class OptimizedPlayer(BaseModel):
    id: int
    name: str
    team: str
    position: str
    projected_points: float
    salary: float
    games_this_week: int

class OptimizedLineup(BaseModel):
    forwards: List[OptimizedPlayer]
    defense: List[OptimizedPlayer]
    goalies: List[OptimizedPlayer]
    total_points: float
    total_salary: float