from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from customwp.views import CustomPage, CustomWaitPage




class StartWP(CustomWaitPage):
    group_by_arrival_time = True
    use_real_effort_task = True
    pay_by_task = 1.5


class Intro(CustomPage):
    ...


class Results(CustomPage):
    ...


page_sequence = [
    StartWP,
    Intro,
    CustomWaitPage,
    Results,
]
