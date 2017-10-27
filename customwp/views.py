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


class CustomPage(Page):
    def extra_condition_to_decorate_is_display(self):
        return not self.player.participant.vars.get('go_to_the_end', False)

    def __init__(self):
        super(CustomPage, self).__init__()

        # We need to edit is_displayed() method dynamically, when creating an instance, since custom use is that it is overriden in the last child
        def decorate_is_displayed(func):
            def decorated_is_display(*args, **kwargs):
                game_condition = func(*args, **kwargs)
                # we need to first run them both separately to make sure that both conditions are executed
                second_condition = self.extra_condition_to_decorate_is_display()
                return game_condition and second_condition

            return decorated_is_display

        setattr(self, "is_displayed", decorate_is_displayed(getattr(self, "is_displayed")))


class CustomWaitPage(WaitPage):
    # Base Mixin... must be used for ALL players pages of our site!!!
    template_name = 'customwp/FirstWaitPage.html'
    use_real_effort_task = False
    pay_by_task = 0
    pay_by_time = 0

    def set_waiting_page_payoff(self, p):
        p.participant.vars.setdefault('ending_time_stamp_{}'.format(self._index_in_pages), time.time())
        current_paying_time = p.participant.vars.get('ending_time_stamp_{}'.format(self._index_in_pages), 0) - \
                              p.participant.vars.get('starting_time_stamp_{}'.format(self._index_in_pages), 0)
        p.participant.vars['total_waiting_time'] = p.participant.vars.get('total_waiting_time',
                                                                          0) + current_paying_time

        p.participant.vars['payment_for_wait'] = p.participant.vars.get('payment_for_wait',
                                                                        0) + p.participant.vars.get(
            "tasks_correct", 0) * self.pay_by_task + current_paying_time * self.pay_by_time

    def dispatch(self, *args, **kwargs):
        curparticipant = Participant.objects.get(code__exact=kwargs['participant_code'])

        if self.request.method == 'POST':
            print('POST HAS BEEN INSERTED')
            curparticipant.vars['go_to_the_end'] = True
            curparticipant.save()
        print('CURPARTICIOANT GAME END', curparticipant.vars.get('go_to_the_end'))
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = time.time()
        if not self.player.startwp_timer_set:
            self.player.startwp_timer_set = True
            self.player.startwp_time = time.time()
        time_left = self.player.startwp_time + Constants.startwp_timer - now
        context.update({
            'index_in_pages': self._index_in_pages,
            'time_left': round(time_left)
        })
        return context

    def extra_task_to_decorate_start_of_after_all_players_arrive(self):
        ...

    def extra_condition_to_decorate_is_display(self):
        self.participant.vars.setdefault('starting_time_stamp_{}'.format(self._index_in_pages), time.time())
        return not self.player.participant.vars.get('go_to_the_end', False)

    def __init__(self):
        super(CustomWaitPage, self).__init__()

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

        setattr(self, "after_all_players_arrive",
                decorate_after_all_players_arrive(getattr(self, "after_all_players_arrive")))

    def extra_task_to_decorate_end_of_after_all_players_arrive(self):
        if self.wait_for_all_groups:
            players = self.subsession.get_players()
            for p in players:
                self.set_waiting_page_payoff(p)

        else:
            players = self.group.get_players()
            for p in players:
                self.set_waiting_page_payoff(p)


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
