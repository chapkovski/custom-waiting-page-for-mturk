from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
from otree.models import Participant
from django.db.models.signals import post_save
from django.dispatch import receiver
from radiogrid import RadioGridField

author = 'Essi Kujansuu - Philipp Chapkovski - Nicolas Gruyer/Economics Games'

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
    endwp_time = models.PositiveIntegerField()


@receiver(post_save, sender=Participant)
def save_participant(sender, instance, **kwargs):
    mturker, created = Mturk.objects.get_or_create(Participant=instance)
    mturker.save()


# THE BIG FIVE QUESTIONS: you can add or eliminate, the code is flexible in terms of number of questions.
ROWS = (
    (1, "Extraverted, enthusiastic"),
    (2, "Critical, quarrelsome"),
    (3, "Dependable, self-disciplined"),
    (4, "Anxious, easily upset"),
    (5, "Open to new experiences, complex"),
    (6, "Reserved, quiet"),
    (7, "Sympathetic, warm"),
    (8, 'Disorganized, careless'),
    (9, 'Calm, emotionally stable'),
    (10, 'Conventional, uncreative'),
    (11, 'Otree Hackathon, hacking'),
)

VALUES = (
    (1, "Disagree strongly"),
    (2, "Disagree moderately"),
    (3, "Disagree a little"),
    (4, "Neither agree nor Disagree"),
    (5, "Agree a little"),
    (6, "Agree moderately"),
    (7, "Agree strongly"),
)


class BigFiveData(djmodels.Model):
    Participant = djmodels.OneToOneField(Participant, on_delete=djmodels.CASCADE,
                                         primary_key=True, related_name="asdf", )
    bigfive = RadioGridField(rows=ROWS, values=VALUES,
                             verbose_name='I see myself as', )
