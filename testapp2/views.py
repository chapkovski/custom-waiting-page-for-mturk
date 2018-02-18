from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage




class StartWP(CustomMturkWaitPage):
    use_task = True
    task='survey'
    # pay by task not implemented for answers to survey yet, but quite simple to adapt
    # pay_by_task = 1.5
    startwp_timer = 12



class Intro(CustomMturkPage):
    ...


class StandardNotCustomWaitPage(WaitPage):
    ...



class Results(CustomMturkPage):
    ...


page_sequence = [
    StartWP,
    Intro,
    StandardNotCustomWaitPage,
    Results,
]
