from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.schemas import schemas
from app.services import optimizer

router = APIRouter()

@router.post("/lineup", response_model=schemas.OptimizedLineup)
async def optimize_lineup(
    settings: schemas.LeagueSettings,
    db: Session = Depends(deps.get_db),
    exclude_players: Optional[List[int]] = None,
    force_players: Optional[List[int]] = None
):
    """
    Generate optimal lineup based on league settings.
    Optionally exclude or force certain players.
    """
    try:
        optimizer_instance = optimizer.FantasyOptimizer(
            db=db,
            settings=settings,
            exclude_players=exclude_players,
            force_players=force_players
        )
        lineup = await optimizer_instance.optimize()
        return lineup
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))