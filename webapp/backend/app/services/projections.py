# app/services/projections.py
from datetime import date
from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict, Optional
from app.core.constants import SEASON_START

class ProjectionService:
    def __init__(self,db: Session, season_start: str = SEASON_START):
        self.db = db
        self.season_start = season_start


    async def create_player_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            print("No player data provided")
            return pd.DataFrame()

        required_columns = ['Date', 'Player', 'Team', 'Goals/60', 'Total Assists/60',
                        'Shots/60', 'ixG/60', 'TOI/GP', 'IPP', 'iHDCF/60']

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return pd.DataFrame()

        try:
            # Note: using self.season_start instead of passed parameter
            def convert_season_format(date_str):
                try:
                    return pd.to_datetime(date_str)
                except:
                    if len(str(date_str)) == 8:
                        year = int(str(date_str)[:4])
                        return pd.to_datetime(f"{year}-01-01")
                    return pd.NaT

            df['Date'] = df['Date'].apply(convert_season_format)

            invalid_dates = df['Date'].isna()
            if invalid_dates.any():
                print(f"Warning: Removed {invalid_dates.sum()} rows with invalid dates")
                df = df[~invalid_dates]

            df = df.sort_values(['Player', 'Date'])

            print(f"Processing data for {df['Player'].nunique()} players")

            current_season = df[df['Date'] >= self.season_start].copy()
            print(f"Found {len(current_season)} records for current season")

            grouped = current_season.groupby('Player')

            stats = ['Goals/60', 'Total Assists/60', 'Shots/60', 'ixG/60',
                    'TOI/GP', 'IPP', 'iHDCF/60']

            for stat in stats:
                print(f"Calculating rolling averages for {stat}")
                current_season[f'{stat}_rolling_5'] = grouped[stat].transform(
                    lambda x: x.rolling(5, min_periods=1).mean()
                )
                current_season[f'{stat}_rolling_10'] = grouped[stat].transform(
                    lambda x: x.rolling(10, min_periods=1).mean()
                )

            recent_stats = current_season.groupby('Player').last().reset_index()
            print(f"Generated features for {len(recent_stats)} players")

            return recent_stats

        except Exception as e:
            print(f"Error processing player features: {e}")
            return pd.DataFrame()

    async def calculate_projections(
        self,
        player_stats: pd.DataFrame,
        games_count: Dict[str, int],
        multipliers: Dict[str, float]
    ) -> pd.DataFrame:
        df = player_stats.copy()

        # Add schedule info
        df['games_this_week'] = df['Team'].map(games_count).fillna(0)
        df['schedule_multiplier'] = df['Team'].map(multipliers).fillna(999.0)

        # Calculate base projections per game
        df['proj_goals_per_game'] = (
            0.4 * df['Goals/60'] +
            0.3 * df['Goals/60_rolling_5'] +
            0.3 * df['Goals/60_rolling_10']
        ) * (df['TOI/GP'] / 60)

        df['proj_assists_per_game'] = (
            0.4 * df['Total Assists/60'] +
            0.3 * df['Total Assists/60_rolling_5'] +
            0.3 * df['Total Assists/60_rolling_10']
        ) * (df['TOI/GP'] / 60)

        # Fill NaN values with 0
        df['proj_goals_per_game'] = df['proj_goals_per_game'].fillna(0)
        df['proj_assists_per_game'] = df['proj_assists_per_game'].fillna(0)

        # Calculate final fantasy points
        df['proj_fantasy_pts'] = (
            (df['proj_goals_per_game'] * 2 +
            df['proj_assists_per_game'] * 1) *
            df['games_this_week'] *
            df['schedule_multiplier']
        )

        # Check for any remaining NaN values
        null_values = df[df['proj_fantasy_pts'].isnull()]
        if not null_values.empty:
            print("\nRows with null projections:")
            print(null_values[['Player', 'Team', 'Position', 'games_this_week', 'schedule_multiplier',
                            'proj_goals_per_game', 'proj_assists_per_game']].head())

        return df

    def get_projection_weights(self) -> Dict[str, float]:
        """
        Get appropriate weights based on time of season
        """
        current_date = date.today()
        season_start_date = pd.to_datetime(self.season_start).date()
        weeks_into_season = ((current_date - season_start_date).days // 7)

        if current_date < season_start_date:
            return self.get_preseason_weights()
        elif weeks_into_season < 4:
            return self.get_early_season_weights(weeks_into_season)
        else:
            return self.get_midseason_weights()

    def get_preseason_weights(self) -> Dict[str, float]:
        """Weights for pre-season projections"""
        return {
            'last_20_games': 0.4,
            'last_season': 0.35,
            'career': 0.25
        }

    def get_early_season_weights(self, weeks_into_season: int) -> Dict[str, float]:
        """Weights that transition from historical to current season"""
        current_season_weight = min(0.7, weeks_into_season * 0.175)  # Gradually increase up to 0.7
        historical_weight = 1 - current_season_weight

        return {
            'current_season': current_season_weight,
            'rolling_5': 0,  # Not enough games yet
            'rolling_10': 0,  # Not enough games yet
            'last_season': historical_weight * 0.7,
            'career': historical_weight * 0.3
        }

    def get_midseason_weights(self) -> Dict[str, float]:
        """Weights for mid-season projections"""
        return {
            'current_season': 0.4,
            'rolling_5': 0.3,
            'rolling_10': 0.3
        }

    async def calculate_weighted_projections(
        self,
        df: pd.DataFrame,
        weights: Dict[str, float]
    ) -> pd.DataFrame:
        # Keep key identifying columns
        key_columns = ['Player', 'Team', 'Position', 'TOI/GP']
        base_df = df[key_columns].drop_duplicates()

        # Split data into current and historical
        current_season = df[df['Date'] >= self.season_start].copy()
        historical = df[df['Date'] < self.season_start].copy()

        # Calculate different stat bases based on available data
        stats = ['Goals/60', 'Total Assists/60']
        projections = {}

        for stat in stats:
            if 'current_season' in weights and not current_season.empty:
                # Current season stats
                current_avg = current_season.groupby('Player')[stat].mean()
                rolling_5 = current_season.groupby('Player')[stat].transform(
                    lambda x: x.rolling(5, min_periods=1).mean()
                ).groupby(current_season['Player']).last()  # Take last value for each player
                rolling_10 = current_season.groupby('Player')[stat].transform(
                    lambda x: x.rolling(10, min_periods=1).mean()
                ).groupby(current_season['Player']).last()  # Take last value for each player

            if not historical.empty:
                # Historical stats
                last_season = historical.groupby('Player')[stat].last()
                career_avg = historical.groupby('Player')[stat].mean()
                last_20 = historical.groupby('Player')[stat].transform(
                    lambda x: x.tail(20).mean()
                ).groupby(historical['Player']).last()  # Take last value for each player

            # Initialize projection with zeros
            projection = pd.Series(0, index=base_df['Player'].unique())

            for weight_type, weight in weights.items():
                if weight_type == 'current_season' and 'current_avg' in locals():
                    projection += weight * current_avg.fillna(0)
                elif weight_type == 'rolling_5' and 'rolling_5' in locals():
                    projection += weight * rolling_5.fillna(0)
                elif weight_type == 'rolling_10' and 'rolling_10' in locals():
                    projection += weight * rolling_10.fillna(0)
                elif weight_type == 'last_season' and 'last_season' in locals():
                    projection += weight * last_season.fillna(0)
                elif weight_type == 'career' and 'career_avg' in locals():
                    projection += weight * career_avg.fillna(0)
                elif weight_type == 'last_20_games' and 'last_20' in locals():
                    projection += weight * last_20.fillna(0)

            projections[stat] = projection

        # Create final projections DataFrame
        proj_df = pd.DataFrame(projections)

        # Merge projections with base information
        final_df = base_df.merge(proj_df, left_on='Player', right_index=True, how='left')

        # Calculate per-game projections
        final_df['proj_goals_per_game'] = (final_df['Goals/60'] * (final_df['TOI/GP'] / 60)).fillna(0)
        final_df['proj_assists_per_game'] = (final_df['Total Assists/60'] * (final_df['TOI/GP'] / 60)).fillna(0)

        return final_df