from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas import schemas
from app.core.constants import MAX_COST, MIN_COST, NUM_FORWARDS, NUM_DEFENSE, NUM_GOALIES, MAX_PLAYERS_PER_TEAM, GOAL, ASSIST, GOALIE_WIN, SHUTOUT, OT_LOSS

router = APIRouter()

@router.get("/default", response_model=schemas.LeagueSettings)
async def get_default_settings():
    """
    Get default league settings
    """
    return {
        "max_salary_cap": MAX_COST,
        "min_salary_cap_pct": MIN_COST,
        "num_forwards": NUM_FORWARDS,
        "num_defense": NUM_DEFENSE,
        "num_goalies": NUM_GOALIES,
        "max_players_per_team": MAX_PLAYERS_PER_TEAM,
        "points_goal": GOAL,
        "points_assist": ASSIST,
        "points_goalie_win": GOALIE_WIN,
        "points_shutout": SHUTOUT,
        "points_ot_loss": OT_LOSS,
        "max_defense_per_team": 1,
        "min_forwards_per_team": 0,
        "max_forwards_per_team": 3,
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