
import time
import channels
import json
import random
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from otree.api import Currency as c, currency_range


from .models import Mturk, WPJobRecord, WPTimeRecord
from otree.common import safe_json
from otree.views.abstract import get_view_from_url
from otree.api import widgets
from otree.models_concrete import (
    PageCompletion, CompletedSubsessionWaitPage,
    CompletedGroupWaitPage, PageTimeout, UndefinedFormModel,
    ParticipantLockModel, GlobalLockModel, ParticipantToPlayerLookup
)
from otree.models import Participant
from . import models
from ._builtin import Page, WaitPage





class DecorateIsDisplayMixin(object):

    def extra_condition_to_decorate_is_display(self):
        # can be overriden, if necessary
        return True

    def extra_task_to_execute_with_is_display(self):
        pass

    def __init__(self):
        super(DecorateIsDisplayMixin, self).__init__()

        # We need to edit is_displayed() method dynamically, when creating an instance, since custom use is that it is overriden in the last child
        def decorate_is_displayed(func):
            def decorated_is_display(*args, **kwargs):
                game_condition = func(*args, **kwargs)
                # we need to first run them both separately to make sure that both conditions are executed
                self.extra_task_to_execute_with_is_display()
                second_condition = self.extra_condition_to_decorate_is_display()
                return game_condition and not self.player.participant.vars.get('go_to_the_end', False) and second_condition

            return decorated_is_display

        setattr(self, "is_displayed", decorate_is_displayed(getattr(self, "is_displayed")))



class CustomPage(DecorateIsDisplayMixin , Page):
    pass


class CustomWaitPage(DecorateIsDisplayMixin , WaitPage):
    # Base Mixin... must be used for ALL players pages of our site!!!
    template_name = 'otree_mturk_utils/CustomWaitPage.html'
    use_real_effort_task = False
    pay_by_task = 0
    pay_by_time = 0
    startwp_timer = 7200

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
            now = time.time()
            time_left = curparticipant.vars.get("startwp_time", 0 ) + self.startwp_timer - now
            if time_left > 0:
                url_should_be_on = curparticipant._url_i_should_be_on()
                return HttpResponseRedirect(url_should_be_on)
            curparticipant.vars['go_to_the_end'] = True
            curparticipant.save()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.core.urlresolvers import resolve
        app_name = self.player._meta.app_label
        index_in_pages = self._index_in_pages
        now = time.time()




        wptimerecord, created = self.participant.mturk.wptimerecord_set.get_or_create(app=app_name, page_index=index_in_pages)
        if not wptimerecord.startwp_timer_set:
            wptimerecord.startwp_timer_set = True
            wptimerecord.startwp_time = time.time()
            wptimerecord.save()
        time_left = wptimerecord.startwp_time + self.startwp_timer - now
        context.update({
            'index_in_pages':index_in_pages,
            'time_left': round(time_left),
            'app_name': app_name
        })
        return context




    def extra_task_to_decorate_start_of_after_all_players_arrive(self):
        ...

    def extra_task_to_execute_with_is_display(self):
        self.participant.vars.setdefault('starting_time_stamp_{}'.format(self._index_in_pages), time.time())

    def __init__(self):
        super(CustomWaitPage, self).__init__()

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


