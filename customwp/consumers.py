from channels import Group
from channels.sessions import channel_session
import random
from .models import Player, Subsession, Constants, Group as OtreeGroup
import json


def send_message(message, group_pk, gbat, index_in_pages):
    those_with_us = Player.objects.filter(
        group__pk=group_pk,
        current_wp=index_in_pages,
    )
    how_many_arrived = len(those_with_us)
    left_to_wait = Constants.players_per_group - how_many_arrived
    textforgroup = json.dumps({
        "how_many_arrived": how_many_arrived,
        "left_to_wait": left_to_wait,
    })
    Group('group_{}'.format(group_pk)).send({
        "text": textforgroup,
    })


def ws_connect(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    print('somebody connected...')
    player = Player.objects.get(pk=player_pk)
    player.current_wp = index_in_pages
    player.save()
    Group('group_{}'.format(group_pk)).add(message.reply_channel)
    send_message(message, group_pk, gbat, index_in_pages)


def ws_message(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    ...


# Connected to websocket.disconnect
def ws_disconnect(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    player = Player.objects.get(pk=player_pk)
    player.current_wp = None
    player.save()
    print('somebody disconnected...')
    Group('group_{}'.format(group_pk)).discard(message.reply_channel)
    send_message(message, group_pk, gbat, index_in_pages)
