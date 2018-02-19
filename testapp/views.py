from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage




class ResultsWaitPage(CustomMturkPage):
# class ResultsWaitPage(CustomMturkWaitPage):
    use_task = True #(by default task is real effort)
    startwp_timer = 12
    pay_by_task=2
    
    def after_all_players_arrive(self):
        pass


class Results(CustomMturkPage):
    pass


# WARNING :: FinalResults inherits only from Page not from CustomMturkPage: Will appear even to players who have hit the "finish study button"
class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

   


page_sequence = [
    ResultsWaitPage,
    Results,
    FinalResults
]
