from channels import Group
from channels.sessions import channel_session
import random
from .models import Player, Subsession, Constants, Group as OtreeGroup
import json



def send_message(message, group_pk, gbat, index_in_pages):
    those_with_us = []
    if gbat:
        those_with_us = Player.objects.filter(
            group__pk=group_pk,
            participant___index_in_pages=index_in_pages,
            _gbat_arrived=True,
            _gbat_grouped=False,
            participant__is_on_wait_page=True,
        )
    else:
        those_with_us = Player.objects.filter(
            participant___index_in_pages=index_in_pages,
            group__pk=group_pk,
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
    Group('group_{}'.format(group_pk)).add(message.reply_channel)
    send_message(message, group_pk, gbat, index_in_pages)


def ws_message(message, participant_code, group_pk, player_pk, index_in_pages, gbat):
    ...



# Connected to websocket.disconnect
def ws_disconnect(message, participant_code, group_pk, player_pk, index_in_pages,gbat):
    print('somebody disconnected...')
    Group('group_{}'.format(group_pk)).discard(message.reply_channel)
    send_message(message, group_pk, gbat, index_in_pages)
