import json
import requests
from datetime import datetime, timedelta

from pytz import timezone

from basketball import Player, Game


def get_players(player_full_name):
    """Search players by their name from balldontlie API.
    Returns a list of found players"""
    names = player_full_name.split(' ')
    get_players_url = ''
    players = []
    if len(names) == 1:
        get_players_url = f'https://www.balldontlie.io/api/v1/players?search={names[0]}'
    elif len(names) == 2:
        get_players_url = f'https://www.balldontlie.io/api/v1/players?search={names[0]}%20{names[1]}'
    response = requests.get(get_players_url)
    response.raise_for_status()
    json_players_data = json.loads(response.text)['data']
    for item in json_players_data:
        if item['height_feet'] is not None and item['weight_pounds'] is not None:
            player = Player(item['id'], item['first_name'], item['last_name'], item['position'],
                            item['height_feet'], item['height_inches'], item['weight_pounds'], item['team'])
            players.append(player)
    return players


def get_player_average_stat(player):
    """Search players' average season stats by their name from balldontlie API.
    Returns a string with stats for each player"""
    get_player_average_url = f'https://www.balldontlie.io/api/v1/season_averages?player_ids[]={player.id}'
    response = requests.get(get_player_average_url)
    response.raise_for_status()
    if json.loads(response.text)['data']:
        json_player_average_data = json.loads(response.text)['data'][0]
        average_stats = f'{player.first_name} {player.last_name}\n' \
                        f'Games played: {json_player_average_data["games_played"]}, ' \
                        f'mins: {json_player_average_data["min"]}\n' \
                        f'fga: {json_player_average_data["fga"]}, fgm: {json_player_average_data["fgm"]}\n' \
                        f'3pa: {json_player_average_data["fg3a"]}, 3pm: {json_player_average_data["fg3m"]}\n' \
                        f'fta: {json_player_average_data["fta"]}, ftm: {json_player_average_data["ftm"]}\n' \
                        f'reb: {json_player_average_data["reb"]}, dreb: {json_player_average_data["dreb"]}, ' \
                        f'oreb: {json_player_average_data["oreb"]}\nast: {json_player_average_data["ast"]}, ' \
                        f'stl: {json_player_average_data["stl"]}, blk: {json_player_average_data["blk"]}\n' \
                        f'turnover: {json_player_average_data["turnover"]}, pts: {json_player_average_data["pts"]}\n' \
                        f'fg%: {"{:.2f}".format(json_player_average_data["fg_pct"] * 100)}%, ' \
                        f'3pt%: {"{:.2f}".format(json_player_average_data["fg3_pct"] * 100)}% ' \
                        f'ft%: {"{:.2f}".format(json_player_average_data["ft_pct"] * 100)}%'
        return average_stats
    return f'No info on {player.first_name} {player.last_name}'


def get_recent_games():
    """Search recently played games from balldontlie API.
    Returns a list of found games"""
    tz = timezone('EST')  # API's time is in EST timezone. Need to convert current time for better precision.
    start_date = (datetime.now(tz) - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = datetime.now(tz).strftime('%Y-%m-%d')
    get_recent_games_url = f'https://www.balldontlie.io/api/v1/games?start_date={start_date}&end_date={end_date}'
    response = requests.get(get_recent_games_url)
    response.raise_for_status()
    json_game_data = json.loads(response.text)['data']
    games = []
    for item in json_game_data:
        if item['period'] != 0:
            game = Game(item["id"], item["home_team"]["abbreviation"], item["visitor_team"]["abbreviation"],
                        item["home_team_score"], item["visitor_team_score"], item["status"])
            games.append(game)
    return games


def get_playing_teams_ids(game_id):
    """Search team ids based on provided game_id.
    Returns ids of home and visitor team"""
    get_game_url = f'https://www.balldontlie.io/api/v1/games/{game_id}'
    response = requests.get(get_game_url)
    response.raise_for_status()
    json_game_data = json.loads(response.text)
    return [json_game_data['home_team']['id'], json_game_data['visitor_team']['id']]


def get_game_stat_for_player(player_full_name):
    """Search players' stat in ant recent games by their name from balldontlie API.
    Returns a string with stats for each player"""
    players = get_players(player_full_name)
    players_stats = []
    recent_games = get_recent_games()
    for game in recent_games:
        playing_teams_ids = get_playing_teams_ids(game.id)
        for player in players:
            if player.team['id'] in playing_teams_ids:
                get_game_player_stat_url = f'https://www.balldontlie.io/api/v1/stats?game_ids[]=' \
                                           f'{game.id}&player_ids[]={player.id}'
                response = requests.get(get_game_player_stat_url)
                response.raise_for_status()
                if json.loads(response.text)['data']:
                    json_player_stat_data = json.loads(response.text)['data'][0]
                    players_stat = f'{player.first_name} {player.last_name}, {game.home_team} vs {game.visitor_team}\n' \
                                   f'mins: {json_player_stat_data["min"]}, pts: {json_player_stat_data["pts"]}\n' \
                                   f'fga: {json_player_stat_data["fga"]}, fgm: {json_player_stat_data["fgm"]}\n' \
                                   f'3pa: {json_player_stat_data["fg3a"]}, 3pm: {json_player_stat_data["fg3m"]}\n' \
                                   f'fta: {json_player_stat_data["fta"]}, ftm: {json_player_stat_data["ftm"]}\n' \
                                   f'reb: {json_player_stat_data["reb"]}, dreb: {json_player_stat_data["dreb"]}, ' \
                                   f'oreb: {json_player_stat_data["oreb"]}\nast: {json_player_stat_data["ast"]}, ' \
                                   f'stl: {json_player_stat_data["stl"]}, blk: {json_player_stat_data["blk"]}\n' \
                                   f'turnover: {json_player_stat_data["turnover"]}, ' \
                                   f'fg%: {json_player_stat_data["fg_pct"]}%, ' \
                                   f'3pt%: {json_player_stat_data["fg3_pct"]}% ' \
                                   f'ft%: {json_player_stat_data["ft_pct"]}%'
                    players_stats.append(players_stat)
    return players_stats
