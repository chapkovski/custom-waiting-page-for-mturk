from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage




class ResultsWaitPage(CustomMturkWaitPage):
# class ResultsWaitPage(CustomMturkWaitPage):
    use_task = True #(by default task is real effort)
    startwp_timer = 12
    pay_by_task=2
    def is_displayed(self):
        return self.round_number == 1  


class Results(CustomMturkPage):
    pass


# Standard not "customMturk" wait page. Exiters will go through this page, because they have been included in a "one player only" group  by the customMurkWaitPage (automatic treatment)
class StandardNotCustomWaitPage(WaitPage):
    pass


# WARNING :: This page is intended to be shown only to participants who previously requested to exit the experiment (on a CustomMturkWaitPage with
# skip_until_the_end_of set to its default value, "experiment")
class PageToShowOnlyToParticipantsWhoExitedTheExp(Page):
       def is_displayed(self):
        return self.round_number == Constants.num_rounds and self.player.participant.vars.get('go_to_the_end')

# WARNING :: FinalResults inherits only from Page not from CustomMturkPage: Will appear even to players who have hit the "finish study button" on a CustomMturkWaitPage
# skip_until_the_end_of
class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

   


page_sequence = [
    ResultsWaitPage,
    Results,
    StandardNotCustomWaitPage,
    PageToShowOnlyToParticipantsWhoExitedTheExp,
    FinalResults
]
