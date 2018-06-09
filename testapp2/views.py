from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage




class StartWP(CustomMturkWaitPage):
    use_task = True
    task='real_effort' 
    # pay_by_task = 1.5 # pay by task not implemented for answers to survey yet, but quite simple to adapt (by analogy with real effort task)
    startwp_timer = 12
    def is_displayed(self):
        return self.round_number == 1  


class Intro(CustomMturkPage):
    pass

# Standard not "customMturk" wait page. Exiters will go through this page, because they have been included in a "one player only" group  by the customMurkWaitPage (automatic treatment)
class StandardNotCustomWaitPage(WaitPage):
    pass



class Results(CustomMturkPage):
    pass


page_sequence = [
    StartWP,
    Intro,
    StandardNotCustomWaitPage,
    Results,
]
