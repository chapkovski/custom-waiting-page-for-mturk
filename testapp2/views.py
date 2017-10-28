from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage




class StartWP(CustomMturkWaitPage):
    group_by_arrival_time = True
    use_real_effort_task = True
    pay_by_task = 1.5
    startwp_timer = 12


class Intro(CustomMturkPage):
    ...


class SecondWaitPage(CustomMturkWaitPage):
    startwp_timer = 600
    # after 10 minutes wait, allow to go to the end
    # otherwise defaults are kept (0 payments no task)
    pass



class Results(CustomMturkPage):
    ...


page_sequence = [
    StartWP,
    Intro,
    SecondWaitPage,
    Results,
]
