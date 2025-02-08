from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.schemas import schemas
from app.services import projections

router = APIRouter()

@router.get("/", response_model=List[schemas.Player])
async def get_players(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retreive players with optional pagination.
    """
    try:
        players = db.query(schemas.Player).offset(skip).limit(limit).all()
        return players
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_player_stats(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve player stats with projections.
    """
    try:
        # TODO: Add projections logic

        return {"message":"Status endpoint - To be implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
