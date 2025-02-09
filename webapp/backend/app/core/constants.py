from datetime import date

def get_season_info():
    current_date = date.today()
    # NHL season typically starts in October
    if current_date.month < 7:  # If we're in first half of calendar year
        season_year = current_date.year
    else:  # If we're in second half of calendar year
        season_year = current_date.year + 1

    season_start = f"{season_year-1}-10-04"  # Approximate season start
    return season_start, season_year

SEASON_START, CURRENT_YEAR = get_season_info()


TEAM_ABBREVIATIONS = {
    'Anaheim Ducks': 'ANA',
    'Boston Bruins': 'BOS',
    'Buffalo Sabres': 'BUF',
    'Calgary Flames': 'CGY',
    'Carolina Hurricanes': 'CAR',
    'Chicago Blackhawks': 'CHI',
    'Colorado Avalanche': 'COL',
    'Columbus Blue Jackets': 'CBJ',
    'Dallas Stars': 'DAL',
    'Detroit Red Wings': 'DET',
    'Edmonton Oilers': 'EDM',
    'Florida Panthers': 'FLA',
    'Los Angeles Kings': 'L.A',
    'Minnesota Wild': 'MIN',
    'Montreal Canadiens': 'MTL',
    'Nashville Predators': 'NSH',
    'New Jersey Devils': 'N.J',
    'New York Islanders': 'NYI',
    'New York Rangers': 'NYR',
    'Ottawa Senators': 'OTT',
    'Philadelphia Flyers': 'PHI',
    'Pittsburgh Penguins': 'PIT',
    'San Jose Sharks': 'S.J',
    'Seattle Kraken': 'SEA',
    'St. Louis Blues': 'STL',
    'Tampa Bay Lightning': 'T.B',
    'Toronto Maple Leafs': 'TOR',
    'Utah Hockey Club': 'UTA',
    'Vancouver Canucks': 'VAN',
    'Vegas Golden Knights': 'VGK',
    'Washington Capitals': 'WSH',
    'Winnipeg Jets': 'WPG'
}

FANTASY_POINTS = {
"GOAL" : 2,
"ASSIST" : 1,
"GOALIE_WIN" : 2,
"SHUTOUT" : 2,
"OT_LOSS" : 1,
"MAX_COST" : 63.00,
"MIN_COST" : "MAX_COST" * 0.99,
"NUM_FORWARDS" : 6,
"NUM_DEFENSE" : 4,
"NUM_GOALIES" : 2,
"MAX_PLAYERS_PER_TEAM" : 5,
"MAX_DEFENSE_PER_TEAM" : 1,
}
