from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
# from otree.api import models as m
from .models import Constants, Player
from otree.common import safe_json
from otree.views.abstract import get_view_from_url
from otree.api import widgets
import random
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from otree.models_concrete import (
    PageCompletion, CompletedSubsessionWaitPage,
    CompletedGroupWaitPage, PageTimeout, UndefinedFormModel,
    ParticipantLockModel, GlobalLockModel, ParticipantToPlayerLookup
)
from otree.models import Participant
import time
import channels
import json


# from .consumers import get_group_name



class CustomWpGenericMixin(object):
    # Base Mixin... must be used for ALL players pages of our site!!!
    use_real_effort_task=False
    pay_by_task = 0
    pay_by_time = 0

    def __init__(self):
        super(CustomWpGenericMixin, self).__init__()
        
        # We need to edit is_displayed() method dynamically, when creating an instance, since custom use is that it is overriden in the last child
        def decorate_is_displayed(func):
            def decorated_is_display(*args, **kwargs):
                game_condition = func(*args, **kwargs) 
                # we need to first run them both separately to make sure that both conditions are executed
                second_condition = self.extra_condition_to_decorate_is_display()
                return game_condition and second_condition
            return decorated_is_display
        setattr(self, "is_displayed", decorate_is_displayed(getattr(self, "is_displayed"))) 
                    # IS A WAIT PAGE
        def decorate_after_all_players_arrive(func):
            def decorated_after_all_players_arrive(*args, **kwargs):
                self.extra_task_to_decorate_start_of_after_all_players_arrive()
                func(*args, **kwargs)
                self.extra_task_to_decorate_end_of_after_all_players_arrive()
            return decorated_after_all_players_arrive
        setattr(self, "after_all_players_arrive", decorate_after_all_players_arrive(getattr(self, "after_all_players_arrive")))

    def extra_condition_to_decorate_is_display(self):
        return not self.player.participant.vars.get('go_to_the_end', False) 

    def extra_task_to_decorate_end_of_after_all_players_arrive(self):




def vars_for_all_templates(self):
    return {'index_in_pages': self._index_in_pages, }
class CustomWaitPage(WaitPage):
    template_name = 'customwp/CustomWaitPage.html'



class CustomPage(Page):
    timeout_seconds = 60

    def is_displayed(self):
        return not self.participant.vars.get('endofgame') and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


class StartWP(CustomWpGenericMixin, CustomWaitPage):
    group_by_arrival_time = True
    template_name = 'customwp/FirstWaitPage.html'
    use_real_effort_task=True
    pay_by_task = 1.5 

    def is_displayed(self):
        return self.subsession.round_number == 1

    def vars_for_template(self):
        now = time.time()
        if not self.player.startwp_timer_set:
            self.player.startwp_timer_set = True
            self.player.startwp_time = time.time()
        time_left = self.player.startwp_time + Constants.startwp_timer - now
        return {'time_left':round(time_left)}

    def dispatch(self, *args, **kwargs):
        curparticipant = Participant.objects.get(code__exact=kwargs['participant_code'])
        if self.request.method == 'POST':
            curparticipant.vars['endofgame'] = True
            curparticipant.save()
        return super().dispatch(*args, **kwargs)

    def get_players_for_group(self, waiting_players):
        endofgamers = [p for p in waiting_players if p.participant.vars.get('endofgame')]
        if endofgamers:
            return endofgamers
        slowpokes = [p.participant for p in self.subsession.get_players()
                     if p.participant._index_in_pages
                     <= self._index_in_pages]
        if len(slowpokes) < Constants.players_per_group:
            self.subsession.not_enough_players = True

        if len(waiting_players) == Constants.players_per_group:
            return waiting_players

    # def is_displayed(self):
    #     return self.round_number == 1


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
