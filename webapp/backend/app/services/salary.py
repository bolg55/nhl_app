from sqlalchemy.orm import Session
import pandas as pd
from ..models import models
from ..core.constants import TEAM_ABBREVIATIONS

class SalaryService:
    def __init__(self, db: Session):
        self.db = db

    async def get_player_salaries(self) -> pd.DataFrame:
        """Get latest player salaries from database"""
        # Using the relationship
        players_with_salaries = (
            self.db.query(models.Player)
            .join(models.PlayerSalary)
            .with_entities(
                models.Player.name.label('Player'),
                models.Player.team.label('Team'),
                models.Player.position.label('Position'),
                models.PlayerSalary.salary.label('pv')
            )
            .order_by(models.PlayerSalary.updated_at.desc())
            .all()
        )

        salary_df = pd.DataFrame(players_with_salaries)
        salary_df['Team'] = salary_df['Team'].map(TEAM_ABBREVIATIONS)

        return salary_df