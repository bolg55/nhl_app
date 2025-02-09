from typing import Tuple
import pandas as pd
from sqlalchemy.orm import Session
from ..core.data_sources import DataSourceFactory

class DataService:
    """Service for managing data sources and retrieval"""

    def __init__(self, db: Session):
        self.db = db
        self.source_factory = DataSourceFactory(db)

    async def get_optimization_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Get all data needed for optimization"""

        # Get data from each source
        player_source = self.source_factory.get_player_stats_source()
        salary_source = self.source_factory.get_salary_source()
        standings_source = self.source_factory.get_standings_source()

        player_data = await player_source.get_data()
        salary_data = await salary_source.get_data()
        standings_data = await standings_source.get_data()

        # Validate data
        if not all([
            await player_source.validate_data(player_data),
            await salary_source.validate_data(salary_data),
            await standings_source.validate_data(standings_data)
        ]):
            raise ValueError("Failed to fetch required data")

        return player_data, salary_data, standings_data