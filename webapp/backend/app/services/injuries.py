from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime
from ..models import models

class InjuryService:
    def __init__(self, db: Session):
        self.db = db

    async def get_current_injuries(self) -> pd.DataFrame:
        """Get active injuries with player information"""
        active_injuries = (
            self.db.query(models.Player)
            .join(models.PlayerInjury)
            .filter(models.PlayerInjury.is_active == True)
            .with_entities(
                models.Player.name.label('Player'),
                models.Player.team.label('Team'),
                models.PlayerInjury.status.label('Injury Status'),
                models.PlayerInjury.expected_return.label('Expected Return')
            )
            .all()
        )

        return pd.DataFrame(active_injuries)