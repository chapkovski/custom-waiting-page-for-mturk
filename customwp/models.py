from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
from otree.models import Participant
from django.db.models.signals import post_save
from django.dispatch import receiver


doc = """
Custom Waiting Pages and Pages for mTurk
"""


class Mturk(djmodels.Model):
    Participant = djmodels.OneToOneField(Participant, on_delete=djmodels.CASCADE,
                                         primary_key=True, )

    current_wp = models.IntegerField()
    outofthegame = models.BooleanField()


class CommonRecord(djmodels.Model):
    mturker = djmodels.ForeignKey(Mturk, on_delete=djmodels.CASCADE)
    app = models.CharField()
    page_index = models.IntegerField()

    class Meta:
        abstract = True


class WPJobRecord(CommonRecord):
    last_correct_answer = models.IntegerField()
    tasks_attempted = models.PositiveIntegerField(initial=0)
    tasks_correct = models.PositiveIntegerField(initial=0)

class WPTimeRecord(CommonRecord):
    startwp_timer_set = models.BooleanField(default=False)
    startwp_time = models.PositiveIntegerField()


@receiver(post_save, sender=Participant)
def save_participant(sender, instance, **kwargs):
    mturker, created = Mturk.objects.get_or_create(Participant=instance)
    mturker.save()




class Constants(BaseConstants):
    # the startwp_timer defines how long the player has to wait at the
    # first waiting page
    # before he or she has an option to finish the game without waiting for
    # others
    startwp_timer = 15


# class Subsession(BaseSubsession):
#     not_enough_players = models.BooleanField(
#         doc=""" this variable set to True when one of the players decide to
#         abandon the game (because he is tired to wait), and
#         there is no enough players left in the session to complete the group.
#         then those remaining get the opportunity to finish the game.""",
#         initial=False
#     )


# class Group(BaseGroup):
#     ...


# class Player(BasePlayer):
#     ...

