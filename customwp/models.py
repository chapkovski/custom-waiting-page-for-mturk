from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
from otree.models import Participant
from django.db.models.signals import post_save
from django.dispatch import receiver


doc = """
...testing timer on waiting page
"""


class Mturk(djmodels.Model):
    Participant = djmodels.OneToOneField(Participant, on_delete=djmodels.CASCADE,
                                         primary_key=True, )

    startwp_timer_set = models.BooleanField(default=False)
    startwp_time = models.PositiveIntegerField()
    current_wp = models.IntegerField()
    outofthegame = models.BooleanField()
    last_correct_answer = models.IntegerField()
    tasks_attempted = models.PositiveIntegerField(initial=0)
    tasks_correct = models.PositiveIntegerField(initial=0)




@receiver(post_save, sender=Participant)
def save_participant(sender, instance, **kwargs):
    mturker, created = Mturk.objects.get_or_create(Participant=instance)
    mturker.save()



class Constants(BaseConstants):
    name_in_url = 'customwp'
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
    ...
    # startwp_timer_set = models.BooleanField(default=False)
    # startwp_time = models.PositiveIntegerField()
    # current_wp = models.IntegerField()
    # outofthegame = models.BooleanField()
    # last_correct_answer = models.IntegerField()
    # tasks_attempted = models.PositiveIntegerField(initial=0)
    # tasks_correct = models.PositiveIntegerField(initial=0)
