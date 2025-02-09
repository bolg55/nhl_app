from sqlalchemy.orm import Session
from app.schemas import schemas
from app.models import models
from .injuries import InjuryService
from .salary import SalaryService
from .goalies import GoalieService
from .schedule import ScheduleService
from .projections import ProjectionService
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

        self.injury_service = InjuryService(db)
        self.salary_service = SalaryService(db)
        self.goalie_service = GoalieService(db)
        self.projection_service = ProjectionService(db)
        self.schedule_service = ScheduleService(db)

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
        """Get player data using SQLAlchemy ORM"""
        player_stats = (
            self.db.query(models.Player)
            .join(models.PlayerStats)
            .with_entities(
                models.Player.name.label('Player'),
                models.Player.team.label('Team'),
                models.Player.position.label('Position'),
                models.PlayerStats.date.label('Date'),
                models.PlayerStats.toi.label('TOI'),
                models.PlayerStats.toi.label('TOI/GP'),  # We might need to calculate this
                models.PlayerStats.goals_per_60.label('Goals/60'),
                models.PlayerStats.assists_per_60.label('Total Assists/60'),
                # Need to add any other columns your projections use
                models.PlayerStats.shots_per_60.label('Shots/60'),
                models.PlayerStats.ixg_per_60.label('ixG/60'),
                # ... any other stats needed for projections
            )
            .filter(models.PlayerStats.date >= date.today() - timedelta(days=365))
            .all()
        )

        return pd.DataFrame(player_stats)

    async def select_best_team(self, df):
        """Your existing optimization logic"""
        # Create a linear programming problem
        prob = pulp.LpProblem("FantasyHockeyTeam", pulp.LpMaximize)

        # Create decision variables
        player_vars = pulp.LpVariable.dicts("player", df.index, cat="Binary")

        # Objective: Maximize total fantasy points
        prob += pulp.lpSum(df['proj_fantasy_pts'][i] * player_vars[i] for i in df.index)

        # Constraints
        # Salary cap
        prob += pulp.lpSum(df['pv'][i] * player_vars[i] for i in df.index) <= self.MAX_COST
        prob += pulp.lpSum(df['pv'][i] * player_vars[i] for i in df.index) >= self.MIN_COST

        # Position requirements
        prob += pulp.lpSum(player_vars[i] for i in df[df['Position'] == 'F'].index) == self.NUM_FORWARDS
        prob += pulp.lpSum(player_vars[i] for i in df[df['Position'] == 'D'].index) == self.NUM_DEFENSE
        prob += pulp.lpSum(player_vars[i] for i in df[df['Position'] == 'G'].index) == self.NUM_GOALIES

        # Max players per team
        teams = df['Team'].unique()
        for team in teams:
            team_player_indices = df[df['Team'] == team].index
            prob += pulp.lpSum(player_vars[i] for i in team_player_indices) <= self.MAX_PLAYERS_PER_TEAM

        # Force/exclude players
        for player_id in self.force_players:
            if player_id in df.index:
                prob += player_vars[player_id] == 1

        for player_id in self.exclude_players:
            if player_id in df.index:
                prob += player_vars[player_id] == 0

        # Solve the problem
        prob.solve(pulp.PULP_CBC_CMD())

        # Extract selected players
        selected_players = [i for i in df.index if player_vars[i].varValue == 1]
        best_team = df.loc[selected_players]

        return best_team

    async def optimize(self):
        """Main optimization function"""
        try:
            # Get player data
            player_data = await self.get_player_data()
            if player_data.empty:
                raise ValueError("No player data available")

            # Get schedule info
            games_count, multipliers = await self.schedule_service.get_weekly_schedule_info()
            if not games_count:
                raise ValueError("Failed to get schedule information")

            remaining_games = sum(games_count.values())
            if remaining_games == 0:
                raise ValueError("No remaining games this week to optimize")

            # Get initial features
            player_features = await self.projection_service.create_player_features(player_data)
            if player_features.empty:
                raise ValueError("Failed to create player features")

            # Get weights based on time of season
            weights = self.projection_service.get_projection_weights()

            # Calculate weighted projections
            projections = await self.projection_service.calculate_weighted_projections(player_features, weights)

            # Add schedule impact
            projections['games_this_week'] = projections['Team'].map(games_count)
            projections['schedule_multiplier'] = projections['Team'].map(multipliers)

            # Calculate final fantasy points
            projections['proj_fantasy_pts'] = (
                (projections['proj_goals_per_game'] * 2 +
                projections['proj_assists_per_game'] * 1) *
                projections['games_this_week'] *
                projections['schedule_multiplier']
            )

            # Filter to active teams
            active_teams = [team for team, count in games_count.items() if count > 0]
            projections = projections[projections['Team'].isin(active_teams)]

            # Add injury information
            injuries_df = await self.injury_service.get_current_injuries()
            if not injuries_df.empty:
                projections = projections.merge(
                    injuries_df[['Player', 'Injury Status']],
                    on='Player',
                    how='left'
                )
                projections['Injured'] = ~projections['Injury Status'].isnull()
                projections.loc[projections['Injured'], 'proj_fantasy_pts'] = 0

            # Add salary information
            salary_df = await self.salary_service.get_player_salaries()
            projections = projections.merge(
                salary_df[['Player', 'Team', 'pv']],
                on=['Player', 'Team'],
                how='left'
            )

            goalie_data = await self.goalie_service.estimate_team_goaltending_points(
                multipliers, games_count
            )
            goalie_df = await self.goalie_service.create_goalie_dataframe(goalie_data)

            # Combine skaters and goalies
            final_df = pd.concat([projections, goalie_df], ignore_index=True)

            # Run optimization
            optimal_lineup = await self.select_best_team(final_df)

            # Format result
            result = schemas.OptimizedLineup(
                forwards=[
                    schemas.OptimizedPlayer(**player)
                    for player in optimal_lineup[optimal_lineup['Position'] == 'F'].to_dict('records')
                ],
                defense=[
                    schemas.OptimizedPlayer(**player)
                    for player in optimal_lineup[optimal_lineup['Position'] == 'D'].to_dict('records')
                ],
                goalies=[
                    schemas.OptimizedPlayer(**player)
                    for player in optimal_lineup[optimal_lineup['Position'] == 'G'].to_dict('records')
                ],
                total_points=float(optimal_lineup['proj_fantasy_pts'].sum()),
                total_salary=float(optimal_lineup['pv'].sum())
            )

            return result

        except Exception as e:
            raise ValueError(f"Optimization failed: {str(e)}")