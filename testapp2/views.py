from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomPage, CustomWaitPage




class StartWP(CustomWaitPage):
    group_by_arrival_time = True
    use_real_effort_task = True
    pay_by_task = 1.5
    startwp_timer = 12


class Intro(CustomPage):
    ...


class SecondWaitPage(CustomWaitPage):
    startwp_timer = 600
    # after 10 minutes wait, allow to go to the end
    # otherwise defaults are kept (0 payments no task)
    pass



class Results(CustomPage):
    ...


page_sequence = [
    StartWP,
    Intro,
    SecondWaitPage,
    Results,
]
