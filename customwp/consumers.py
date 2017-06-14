from channels import Group
from channels.sessions import channel_session
import random
from .models import Player, Subsession, Constants
import json
import time
from otree.views.abstract import get_view_from_url


def get_group_name(subsession_pk, index_in_pages, player_pk):
    curplayer = Player.objects.get(pk=player_pk)
    group_pk = curplayer.group.pk
    group_name = 'mturkchannel_{}_{}_{}'.format(subsession_pk,
                                                index_in_pages,
                                                group_pk
                                                )
    return group_name


def send_message(message, subsession, index_in_pages, player_pk, ):
    curplayer = Player.objects.get(pk=player_pk)
    url = curplayer.participant._url_i_should_be_on()
    Page = get_view_from_url(url)
    those_with_us = []
    if hasattr(Page, 'group_by_arrival_time'):
        if getattr(Page, 'group_by_arrival_time'):
            those_with_us = Player.objects.filter(
                subsession=subsession,
                participant___index_in_pages=index_in_pages,
                _group_by_arrival_time_arrived=True,
                _group_by_arrival_time_grouped=False,
            )
        else:
            those_with_us = Player.objects.filter(
                subsession=subsession,
                participant___index_in_pages=index_in_pages,
                group=curplayer.group,
            )

    how_many_arrived = len(those_with_us)
    left_to_wait = Constants.players_per_group - how_many_arrived
    textforgroup = json.dumps({
                                "how_many_arrived": how_many_arrived,
                                "left_to_wait": left_to_wait,
                                })
    Group(get_group_name(subsession, index_in_pages, player_pk)).send({
        "text": textforgroup,
    })


def ws_connect(message, subsession, index_in_pages, player_pk):
    cursubsession = Subsession.objects.get(pk=subsession)
    print('somebody connected...')
    Group(get_group_name(subsession, index_in_pages, player_pk)).add(message.reply_channel)
    send_message(message, subsession, index_in_pages, player_pk)


def ws_message(message, subsession, index_in_pages, player_pk):
    ...
    # textforgroup = json.dumps({"LastPlayers": True, })
    # Group(get_group_name(subsession, index_in_pages, player_pk)).send({
    #     "text": textforgroup,
    # })


# Connected to websocket.disconnect
def ws_disconnect(message, subsession, index_in_pages, player_pk):
    print('somebody disconnected...')
    Group(get_group_name(subsession, index_in_pages, player_pk)).discard(message.reply_channel)
    send_message(message, subsession, index_in_pages, player_pk)
