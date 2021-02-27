class Player:
    """A basketball player class"""
    def __init__(self, id_, first_name, last_name, position, height_feet, height_inches,
                 weight_pounds, team):
        self.id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.height_feet = height_feet
        self.height_inches = height_inches
        self.position = position
        self.weight_pounds = weight_pounds
        self.team = team

    def __str__(self):
        height = f'Height: {self.height_feet}\'{self.height_inches}'
        weight = f'weight: {self.weight_pounds} pounds'
        return f'{self.first_name} {self.last_name}, position: {self.position}\n' \
               f'Team: {self.team["full_name"]}, conference: {self.team["conference"]}\n' \
               f'{height}, {weight}'


class Game:
    """A basketball game class"""
    def __init__(self, id_, home_team, visitor_team, home_team_score, visitor_team_score, status):
        self.id = id_
        self.home_team = home_team
        self.visitor_team = visitor_team
        self.home_team_score = home_team_score
        self.visitor_team_score = visitor_team_score
        self.status = status

    def __str__(self):
        return f'{self.home_team} vs {self.visitor_team}\n' \
               f'{self.home_team_score}-{self.visitor_team_score}\n' \
               f'Status: {self.status}'
