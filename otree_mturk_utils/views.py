import time
import ast

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm

from otree.common_internal import get_models_module
from otree.models import Participant
from . import models
from ._builtin import Page, WaitPage


class BigFiveForm(ModelForm):
    class Meta:
        model = models.BigFiveData
        fields = ['bigfive']


class DecorateIsDisplayMixin(object):

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

                app_name = self.player._meta.app_label
                round_number = self.player.round_number
                return game_condition and not self.player.participant.vars.get('go_to_the_end',
                                                                               False) and not self.player.participant.vars.get('skip_the_end_of_app_{}'.format(app_name),
                                                                               False) and not self.player.participant.vars.get('skip_the_end_of_app_{}_round_{}'.format(app_name , round_number),
                                                                               False) 

            return decorated_is_display

        setattr(self, "is_displayed", decorate_is_displayed(getattr(self, "is_displayed")))


class CustomMturkPage(DecorateIsDisplayMixin, Page):
    pass


class CustomMturkWaitPage(WaitPage):
    # Only for the first, grouping wait page of the app
    template_name = 'otree_mturk_utils/CustomWaitPage.html'

    # Deault attributes
    use_task = False
    # How much the participant should be payed by second spent on the wait page, and by task done. The result will be stored in participant.vars['payment_for_wait']
    pay_by_task = 0
    pay_by_time = 0
    # In case a player waits more than startwp_timer (expressed in seconds), he will be offered the option to skip pages. By default, if skip_until_the_end_of = "experiment", if he decides to skip pages, he will skip all the pages untill the end of the experiment (provided those pages inherit from CustomMturkPage or CustomMturkWaitPage).
    # If skip_until_the_end_of = "app", he will only skip the pages of the current app. If skip_until_the_end_of = "round", only pages of the current round will be skipped
    startwp_timer = 7200
    # "experiment" or "app or "round"
    skip_until_the_end_of = "experiment"

    task = 'real_effort' # choice between 'survey' and 'real_effort'

    group_by_arrival_time = True


    def set_waiting_page_payoff(self, p):
        p.participant.vars.setdefault('ending_time_stamp_{}'.format(self._index_in_pages), time.time())
        current_paying_time = p.participant.vars.get('ending_time_stamp_{}'.format(self._index_in_pages), 0) - \
                              p.participant.vars.get('starting_time_stamp_{}'.format(self._index_in_pages), 0)
        p.participant.vars['total_waiting_time'] = p.participant.vars.get('total_waiting_time',
                                                                          0) + current_paying_time

        correct_tasks = 0
        attempted_tasks = 0
        try:
            mturker = models.Mturk.objects.get(Participant__code=p.participant.code)
            wprecord= mturker.wpjobrecord_set.get(app=p._meta.app_label, page_index=self._index_in_pages)
            correct_tasks = wprecord.tasks_correct
            attempted_tasks = wprecord.tasks_attempted
        except ObjectDoesNotExist:
            pass

        p.participant.vars['payment_for_wait'] = p.participant.vars.get('payment_for_wait',0) + correct_tasks * self.pay_by_task + current_paying_time * self.pay_by_time
   

    def dispatch(self, *args, **kwargs):

        curparticipant = Participant.objects.get(code__exact=kwargs['participant_code'])

        if self.request.method == 'POST':
            now = time.time()
            time_left = curparticipant.vars.get("startwp_time", 0) + self.startwp_timer - now
            if time_left > 0:
                url_should_be_on = curparticipant._url_i_should_be_on()
                return HttpResponseRedirect(url_should_be_on)

            if self.skip_until_the_end_of in ["app" , "round"]:
                app_name = curparticipant._current_app_name
                if self.skip_until_the_end_of == "round" :
                    round_number = curparticipant._round_number
                    curparticipant.vars['skip_the_end_of_app_{}_round_{}'.format(app_name , round_number)] = True
                else:
                    # "app"
                    curparticipant.vars['skip_the_end_of_app_{}'.format(app_name)] = True
            else :
                assert self.skip_until_the_end_of == "experiment" , "the attribute skip_until_the_end_of should be set to experiment, app or round, not {}".format(self.skip_until_the_end_of)
                curparticipant.vars['go_to_the_end'] = True
   
            curparticipant.save()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_name = self.player._meta.app_label
        index_in_pages = self._index_in_pages
        now = time.time()

        wptimerecord, created = self.participant.mturk.wptimerecord_set.get_or_create(app=app_name,
                                                                                      page_index=index_in_pages)
        if not wptimerecord.startwp_timer_set:
            wptimerecord.startwp_timer_set = True
            wptimerecord.startwp_time = time.time()
            wptimerecord.save()
        time_left = wptimerecord.startwp_time + self.startwp_timer - now
        time_passed = now - wptimerecord.startwp_time
        if self.use_task:
            if self.task == 'real_effort':
                task_to_show = 'otree_mturk_utils/RealEffortTask'
            else:
                task_to_show = 'otree_mturk_utils/BigFive'
                num_questions = len(models.ROWS)
                f = BigFiveForm()
                data, created = models.BigFiveData.objects.get_or_create(Participant=self.player.participant)
                if created:
                    old_data = []
                else:
                    old_data = data.bigfive
                context.update({'num_questions': num_questions,
                                'old_data': old_data,
                                'myform': f})
            task_to_show = {'js': '{}.js'.format(task_to_show), 'html': '{}.html'.format(task_to_show)}
            context.update({
                'task_to_show': task_to_show,
            })

        context.update({
            'use_task':self.use_task,
            'index_in_pages': index_in_pages,
            'time_left': round(time_left),
            'time_passed': round(time_passed),
            'app_name': app_name,
        })
        return context









    def __init__(self):
        super(CustomMturkWaitPage, self).__init__()

        # IS A WAIT PAGE
        def decorate_after_all_players_arrive(func):
            def decorated_after_all_players_arrive(*args, **kwargs):
                self.extra_task_to_decorate_start_of_after_all_players_arrive()
                func(*args, **kwargs)
                self.extra_task_to_decorate_end_of_after_all_players_arrive()

            return decorated_after_all_players_arrive

        setattr(self, "after_all_players_arrive",
                decorate_after_all_players_arrive(getattr(self, "after_all_players_arrive")))




        # We need to edit is_displayed() method dynamically, when creating an instance, since custom use is that it is overriden in the last child
        def decorate_is_displayed(func):
            def decorated_is_display(*args, **kwargs):
                game_condition = func(*args, **kwargs)
                # we need to first run them both separately to make sure that both conditions are executed
                self.extra_task_to_execute_with_is_display()
                return game_condition 
            return decorated_is_display

        setattr(self, "is_displayed", decorate_is_displayed(getattr(self, "is_displayed")))


        def decorate_get_players_for_group(func):
            def decorated_get_players_for_group(*args, **kwargs):
                grouped = self.extra_task_to_decorate_start_of_get_players_for_group(*args, **kwargs)
                if grouped:
                    # form groups of only one when a players decides to finish the experiment--> otherwise , there might be problems later during ordinary wait pages
                    return grouped[0:1]
                grouped = func(*args, **kwargs)
                if grouped:
                    return grouped
                grouped = self.extra_task_to_decorate_end_of_get_players_for_group(*args, **kwargs)
                if grouped:
                    return grouped

            return decorated_get_players_for_group

        setattr(self, "get_players_for_group",
                decorate_get_players_for_group(getattr(self, "get_players_for_group")))



    def extra_task_to_decorate_start_of_get_players_for_group(self, waiting_players):
        app_name = self.subsession._meta.app_label
        round_number = self.subsession.round_number
        endofgamers = [p for p in waiting_players if (
            p.participant.vars.get('go_to_the_end') or p.participant.vars.get('skip_the_end_of_app_{}'.format(app_name)) or p.participant.vars.get('skip_the_end_of_app_{}_round_{}'.format(app_name , round_number))
            )]
        if endofgamers:
            return endofgamers


    def extra_task_to_decorate_end_of_get_players_for_group(self, waiting_players):
        app_name = self.subsession._meta.app_label
        if len(waiting_players) == get_models_module(app_name).Constants.players_per_group:
            return waiting_players



    def extra_task_to_decorate_start_of_after_all_players_arrive(self):
        ...


    def extra_task_to_decorate_end_of_after_all_players_arrive(self):
        if self.wait_for_all_groups:
            players = self.subsession.get_players()
            for p in players:
                self.set_waiting_page_payoff(p)

        else:
            players = self.group.get_players()
            for p in players:
                self.set_waiting_page_payoff(p)


    def extra_task_to_execute_with_is_display(self):
        self.participant.vars.setdefault('starting_time_stamp_{}'.format(self._index_in_pages), time.time())




        
