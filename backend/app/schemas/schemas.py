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
    max_salary_cap: float
    num_forwards: int
    num_defense: int
    num_goalies: int
    points_goal: float
    points_assist: float
    points_goalie_win: float

class LeagueSettingsCreate(LeagueSettingsBase):
    pass

class LeagueSettings(LeagueSettingsBase):
    id: int

    class Config:
        from_attributes = True