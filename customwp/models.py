from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
# from settings import SESSION_CONFIGS


doc = """
...testing timer on waiting page
"""


class Constants(BaseConstants):
    name_in_url = 'cusotomwp'
    players_per_group = 3
    num_rounds = 1
    # the startwp_timer defines how long the player has to wait at the
    # first waiting page
    # before he or she has an option to finish the game without waiting for
    # others
    startwp_timer = 15


class Subsession(BaseSubsession):
    not_enough_players = models.BooleanField(
        doc=""" this variable set to True when one of the players decide to
        abandon the game (because he is tired to wait), and
        there is no enough players left in the session to complete the group.
        then those remaining get the opportunity to finish the game.""",
        initial=False
    )


class Group(BaseGroup):
    ...


class Player(BasePlayer):
    startwp_timer_set = models.BooleanField(default=False)
    startwp_time = models.PositiveIntegerField()
    current_wp = models.IntegerField()
    outofthegame = models.BooleanField()
