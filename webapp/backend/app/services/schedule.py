from sqlalchemy.orm import Session
from datetime import date, timedelta
import pandas as pd
from app.models import models
from app.core.constants import TEAM_ABBREVIATIONS, CURRENT_YEAR


async def fetch_game_data(year: int):
    """Fetches NHL games and teams involved for a given year."""
    url = f"https://www.hockey-reference.com/leagues/NHL_{year}_games.html"
    dfs = pd.read_html(url)
    df = dfs[0]

    # Convert the "Date" column to datetime.date format
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Extract relevant columns
    game_data = df[["Date", "Visitor", "Home"]]

    return game_data

async def filter_dates_for_week(dates, start_date):
    """Filter dates for current week's remaining games."""
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    end_date = start_date + timedelta(days=6)
    today = date.today()

    # Filter for dates in the week AND in the future
    week_dates = [d for d in dates if start_date <= d <= end_date and d >= today]

    return week_dates

async def games_count_for_team_for_week(year: int, start_date: date):
    """Get number of games per team for the week."""
    game_data = await fetch_game_data(year)

    week_dates = await filter_dates_for_week(game_data["Date"].tolist(), start_date)
    week_games = game_data[game_data["Date"].isin(week_dates)]

    visitor_counts = week_games["Visitor"].value_counts().to_dict()
    home_counts = week_games["Home"].value_counts().to_dict()

    total_counts = {}
    for team in set(list(visitor_counts.keys()) + list(home_counts.keys())):
        total_counts[team] = visitor_counts.get(team, 0) + home_counts.get(team, 0)

    return total_counts


async def get_weekly_schedule_info(db: Session, start_date=date.today()):
    """Get schedule information for remaining games this week"""

    # Get games per team
    games_count_full = await games_count_for_team_for_week(CURRENT_YEAR, start_date)

    # Convert full team names to abbreviations
    games_count = {TEAM_ABBREVIATIONS[team]: count
                  for team, count in games_count_full.items()
                  if team in TEAM_ABBREVIATIONS}

    # Get team standings from database
    standings = db.query(models.TeamStandings).all()
    points_df = pd.DataFrame([{
        'Team': s.team,
        'PTS%': s.points_percentage,
    } for s in standings])

    # Calculate multipliers
    multipliers = {}
    for team, count in games_count.items():
        if count > 0:
            team_row = points_df[points_df['Team'] == team]
            if not team_row.empty:
                multipliers[team] = 0.5 / team_row['PTS%'].iloc[0]

    return games_count, multipliers