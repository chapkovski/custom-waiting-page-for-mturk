from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage

class MyPage(CustomMturkPage):
    pass


class ResultsWaitPage(CustomMturkWaitPage):
    use_real_effort_task = True
    startwp_timer = 12
    
    def after_all_players_arrive(self):
        pass


class Results(CustomMturkPage):
    pass


page_sequence = [
    MyPage,
    ResultsWaitPage,
    Results,
    ResultsWaitPage,
]
