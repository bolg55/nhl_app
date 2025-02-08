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
        "num_forwards": 6,
        "num_defense": 4,
        "num_goalies": 2,
        "points_goal": 2.0,
        "points_assist": 1.0,
        "points_goalie_win": 2.0
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