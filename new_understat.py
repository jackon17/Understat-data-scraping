from understatapi import UnderstatClient
from fuzzywuzzy import process
from prettytable import PrettyTable

def extract_league_data():
    league_names = ["EPL", "Bundesliga", "La_Liga", "Serie_A", "Ligue_1"]
    leagues = {}
    for league in league_names:
        leagues[league] = understat.league(league=league).get_player_data("2025")
    return leagues

def search_by_name(player_name: str, leagues: dict):
    for league in leagues.values():
        for player in league:
            if player["player_name"].lower() == player_name.lower():
                print("")
                print(f"{player_name.title()} (Understat ID: {player["id"]})")
                recent_seasons = understat.player(player["id"]).get_season_data()["season"][:5]
                return recent_seasons

def fuzzy_matches(player_name: str, leagues: dict):
    print("")
    print("Checking possible matches...")
    closest = []
    for league in leagues.values():
        names = [player["player_name"] for player in league]
        close = [name for name in process.extract(player_name, names) if name[1] >= 80]
        for item in close:
            closest.append(item)
    closest.sort(reverse=True, key=lambda x: x[1]) # sort matches by closest matches
    closest = closest[:5]
    for i in range(len(closest)):
        print(f"{i + 1}. {closest[i][0]}")
    try:
        number = int(input("Are you looking for any of these players? (Input matching number, or blank): "))
        return closest[number - 1][0]
    except:
        return False

def make_table(recent_seasons: dict):
    headers = ["season", "team", "games", "goals", "assists"]
    table = PrettyTable(headers)
    for season in recent_seasons:
        row = []
        for header in headers:
            row.append(season[header])
        table.add_row(row)
    return table

if __name__ == "__main__":
    
    understat = UnderstatClient()
    
    while True:
        player_name = input("Please input a player name: ")

        print("")
        print("Searching player database...")

        leagues = extract_league_data()

        seasons = search_by_name(player_name, leagues)

        if seasons:
            break

        match = fuzzy_matches(player_name, leagues)

        if match:
            seasons = search_by_name(match, leagues)
            break

        print("Please try again.")
        print(" ")

    print(make_table(seasons))

