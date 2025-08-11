from understatapi import UnderstatClient
from bs4 import BeautifulSoup
from fuzzywuzzy import process

def search_by_name(player_name: str): 
    leagues = ["EPL", "Bundesliga", "La_Liga", "Serie_A", "Ligue_1"]
    for league in leagues:
        league_player_data = understat.league(league=league).get_player_data("2024")
        for player in league_player_data:
            if player["player_name"] == player_name:
                print(f"{player_name}'s Understat ID is {player["id"]}")
                return player["id"]

def fuzzy_matches(player_name: str):
    print("Checking possible matches...")
    leagues = ["EPL", "Bundesliga", "La_Liga", "Serie_A", "Ligue_1"]
    closest = []
    for league in leagues:
        league_player_data = understat.league(league=league).get_player_data("2024")       
        names = [item["player_name"] for item in league_player_data]
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

def create_table(player_id: str):
    recent_seasons = understat.player(player_id).get_season_data()["season"][:5]

    soup = BeautifulSoup('<html><body><table border="1"></table></body></html>', 'html.parser')
    table = soup.find('table') # finds the first <table> tag in the HTML, saves it to table variable

    if recent_seasons:
        headers = ['season', 'team', 'games', 'goals', 'assists']
        header_row = soup.new_tag('tr') # initialises header row in the table
        for header in headers:
            th = soup.new_tag('th')
            th.string = header # adds string to the header tag
            header_row.append(th) # adds the header tag to the header row
        table.append(header_row)

        # Add data rows
        for season in recent_seasons:
            row = soup.new_tag('tr')
            for key in headers:
                td = soup.new_tag('td')
                td.string = str(season.get(key, 'N/A')) # gets season, team etc from the season data
                row.append(td)
            table.append(row)
        
    return soup

def write_to_file(soup: BeautifulSoup):
    with open("table.html", "w") as file:
        file.write(str(soup.prettify()))
    print("Data table succesfully written to 'table.html'")

if __name__ == "__main__":
    
    understat = UnderstatClient()
    
    while True:
        player_name = input("Please input a player name: ")
        print("Searching player database...")
        player_id = search_by_name(player_name)

        if player_id:
            break

        match = fuzzy_matches(player_name)

        if match:
            player_id = search_by_name(match)
            break

        print("Please try again.")
        print(" ")
    
    print("Extracting data...") 
    
    soup = create_table(player_id)

    write_to_file(soup)