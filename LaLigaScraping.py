import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

all_teams = []  # list to store all teams

# getting the html from the website
html = requests.get('https://fbref.com/en/comps/12/La-Liga-Stats').text
soup = BeautifulSoup(html, 'lxml')
# only want the first table, therefore the first index
table = soup.find_all('table', class_='stats_table')[0]

links = table.find_all('a')  # finding all links in the table
links = [l.get("href") for l in links]  # parsing through links
# filtering through links to only get squads
links = [l for l in links if '/squads/' in l]

# formatting back to links
team_urls = [f"https://fbref.com{l}" for l in links]

for team_url in team_urls:
    # isolating the names of the teams
    team_name = team_url.split("/")[-1].replace("-Stats", "")
    data = requests.get(team_url).text
    soup = BeautifulSoup(data, 'lxml')
    stats = soup.find_all('table', class_="stats_table")[
        0]  # again, only want the first table

    if stats and stats.columns:
        stats.columns = stats.columns.droplevel()  # formatting the stats

    # Convert the BeautifulSoup tag to a DataFrame
    team_data = pd.read_html(str(stats))[0]
    team_data["Team"] = team_name
    all_teams.append(team_data)  # appending the data
    # delay each loop by 5 seconds to avoid getting blocked
    time.sleep(5)

stat_df = pd.concat(all_teams)  # concatenating all of the stats
# specifying UTF-8 encoding with BOM
stat_df.to_csv("stats.csv", encoding='utf-8-sig', index=False)
