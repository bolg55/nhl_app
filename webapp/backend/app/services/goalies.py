from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict, Tuple
from ..core.constants import GOALIE_WIN, SHUTOUT, OT_LOSS

class GoalieService:
    def __init__(self, db: Session):
        self.db = db

    async def estimate_team_goaltending_points(
        self,
        multipliers: Dict[str, float],
        games_count: Dict[str, int],
        win_points: float = GOALIE_WIN,
        shutout_bonus: float = SHUTOUT,
        ot_loss_points: float = OT_LOSS,
        avg_shutout_freq: float = 0.05,
        avg_ot_loss_freq: float = 0.1
    ) -> Dict[str, Tuple[float, int]]:
        """Calculate projected goalie points for each team"""
        goaltending_data = {}

        for team, multiplier in multipliers.items():
            games = games_count.get(team, 0)

            # Estimate wins based on multiplier (inverse relation)
            projected_wins = games / multiplier if multiplier > 0 else 0
            projected_shutouts = games * avg_shutout_freq

            total_points = (
                projected_wins * win_points +
                projected_shutouts * shutout_bonus +
                avg_ot_loss_freq * ot_loss_points
            )

            goaltending_data[team] = (total_points, games)

        return goaltending_data

    async def create_goalie_dataframe(
        self,
        goalie_data: Dict[str, Tuple[float, int]]
    ) -> pd.DataFrame:
        """Convert goalie projections to DataFrame format"""
        goalie_rows = []
        for team, (points, games) in goalie_data.items():
            goalie_rows.append({
                'Player': f"{team} Goaltending",
                'Team': team,
                'Position': 'G',
                'games_this_week': games,
                'proj_fantasy_pts': points,
                'pv': 0.0,  # Goalies don't count against salary cap
                'Injured': False
            })

        return pd.DataFrame(goalie_rows)