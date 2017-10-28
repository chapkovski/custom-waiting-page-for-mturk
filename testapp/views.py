from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from customwp.views import CustomPage, CustomWaitPage

class MyPage(CustomPage):
    pass


class ResultsWaitPage(CustomWaitPage):
    use_real_effort_task = True
    def after_all_players_arrive(self):
        pass


class Results(CustomPage):
    pass


page_sequence = [
    MyPage,
    ResultsWaitPage,
    Results,
    ResultsWaitPage,
]
