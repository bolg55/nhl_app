from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import schemas

router = APIRouter()

@router.get("/default", response_model=schemas.LeagueSettings)
async def get_default_settings():
    """
    Get default league settings
    """
    return {
        "max_salary_cap": 63.0,
        "min_salary_cap_pct": 0.99,
        "num_forwards": 6,
        "num_defense": 4,
        "num_goalies": 2,
        "max_players_per_team": 5,
        "points_goal": 2.0,
        "points_assist": 1.0,
        "points_goalie_win": 2.0,
        "max_defense_per_team": 1,
        "min_forwards_per_team": 0,
        "max_forwards_per_team": None,
    }

@router.post("/", response_model=schemas.LeagueSettings)
async def create_settings(
    settings: schemas.LeagueSettings,
    db: Session = Depends(deps.get_db)
):
    """
    Create or update league settings
    """
    try:
        # Save settings to database
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))