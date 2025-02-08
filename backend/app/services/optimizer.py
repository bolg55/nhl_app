from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models import models
import pulp
import pandas as pd
from datetime import date, timedelta
from typing import List, Optional

class FantasyOptimizer:
    def __init__(
            self,
            db: Session,
            settings: schemas.LeagueSettings,
            exclude_players: Optional[List[int]] = None,
            force_players: Optional[List[int]] = None,
    ):
        self.db = db
        self.settings = settings
        self.exclude_players = exclude_players or []
        self.force_players = force_players or []

        # Constants
        self.MAX_COST = settings.max_salary_cap
        self.MIN_COST = self.MAX_COST * settings.min_salary_cap_pct
        self.NUM_FORWARDS = settings.num_forwards
        self.NUM_DEFENSE = settings.num_defense
        self.NUM_GOALIES = settings.num_goalies
        self.MAX_PLAYERS_PER_TEAM = settings.max_players_per_team

        #  Additional settings
        if settings.max_defense_per_team:
            self.MAX_DEFENSE_PER_TEAM = settings.max_defense_per_team

    async def get_player_data(self):
        # Get player data from database

        query = """
        SELECT * FROM player_data
        WHERE Date >= :start_date
        """
        df = pd.read_sql(query, self.db.bind, params={"start_date": date.today() - timedelta(days=365)})
        return df