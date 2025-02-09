from typing import Optional, Dict, Any, Union
import pandas as pd
from sqlalchemy.orm import Session
from pydantic import BaseModel

class DataSourceConfig(BaseModel):
    """Configuration for a data source"""
    type: str
    params: Dict[str, Any] = {}

class BaseDataSource:
    """Base class for all data sources"""

    async def get_data(self) -> pd.DataFrame:
        """Fetch data from the source"""
        raise NotImplementedError

    async def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate the data meets requirements"""
        return not df.empty

class DatabaseDataSource(BaseDataSource):
    """Handles data from database"""

    def __init__(self, db: Session, query: str, params: Dict[str, Any] = None):
        self.db = db
        self.query = query
        self.params = params or {}

    async def get_data(self) -> pd.DataFrame:
        try:
            df = pd.read_sql(self.query, self.db.bind, params=self.params)
            return df
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            return pd.DataFrame()

class DataSourceFactory:
    """Factory for creating data sources"""

    def __init__(self, db: Session):
        self.db = db

    def get_player_stats_source(self) -> DatabaseDataSource:
        query = """
        SELECT *
        FROM player_data
        WHERE Date >= :start_date
        """
        return DatabaseDataSource(
            db=self.db,
            query=query,
            params={"start_date": "2019-10-01"}
        )

    def get_salary_source(self) -> DatabaseDataSource:
        query = """
        SELECT
            p.name as Player,
            p.team as Team,
            p.position as Position,
            ps.salary as pv
        FROM players p
        JOIN player_salaries ps ON p.id = ps.player_id
        ORDER BY ps.updated_at DESC
        """
        return DatabaseDataSource(self.db, query)

    def get_standings_source(self) -> DatabaseDataSource:
        query = """
        SELECT
            team,
            points_percentage
        FROM team_standings
        """
        return DatabaseDataSource(self.db, query)
