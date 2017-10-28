from channels import Group
from channels.sessions import channel_session
import random
from .models import Constants, Mturk
import json
import random
from random import randint
from django.core.exceptions import ObjectDoesNotExist
from otree.models import Participant
from importlib import import_module

def get_models_module(app_name):
    module_name = '{}.models'.format(app_name)
    return import_module(module_name)

# ============= For creating a task
def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_random_list():
    max_len = 100
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


def get_task():
    string_len = 10
    listx = get_random_list()
    listy = get_random_list()
    answer = max(listx) + max(listy)
    listx = slicelist(listx, string_len)
    listy = slicelist(listy, string_len)
    return {
        "message_type": "new_task",
        "mat1": listx,
        "mat2": listy,
        "correct_answer": answer,
    }


def send_message(message,app_name, group_pk, gbat, index_in_pages):

    those_with_us = get_models_module(app_name).Player.objects.filter(
        group__pk=group_pk,
        participant__mturk__current_wp=index_in_pages,
    )
    how_many_arrived = len(those_with_us)
    left_to_wait = Constants.players_per_group - how_many_arrived
    textforgroup = json.dumps({
        "message_type": "players_update",
        "how_many_arrived": how_many_arrived,
        "left_to_wait": left_to_wait,
    })
    Group('group_{}'.format(group_pk)).send({
        "text": textforgroup,
    })


def ws_connect(message, participant_code,app_name, group_pk, player_pk, index_in_pages, gbat):
    print('somebody connected...')
    try:
        mturker = Mturk.objects.get(Participant__code=participant_code)
    except ObjectDoesNotExist:
        return None
    mturker.current_wp = index_in_pages
    new_task = get_task()
    mturker.last_correct_answer = new_task['correct_answer']
    mturker.save()
    message.reply_channel.send({'text': json.dumps(new_task)})

    Group('group_{}'.format(group_pk)).add(message.reply_channel)
    send_message(message, app_name, group_pk, gbat, index_in_pages)


def ws_message(message, participant_code, app_name,group_pk, player_pk, index_in_pages, gbat):
    jsonmessage = json.loads(message.content['text'])
    answer = jsonmessage.get('answer')
    if answer:
        try:
            player =get_models_module(app_name).Player.objects.get(pk=player_pk, participant__code=participant_code)
        except ObjectDoesNotExist:
            return None

        add_one(player, "tasks_attempted")

        player.tasks_attempted += 1
        if int(answer) == int(player.last_correct_answer):
            player.tasks_correct += 1
            add_one(player, "tasks_correct")

        new_task = get_task()
        new_task['tasks_correct'] = player.tasks_correct
        new_task['tasks_attempted'] = player.tasks_attempted
        player.last_correct_answer = new_task['correct_answer']
        player.save()
        message.reply_channel.send({'text': json.dumps(new_task)})



# Connected to websocket.disconnect
def ws_disconnect(message, participant_code, app_name, group_pk, player_pk, index_in_pages, gbat):
    try:
        mturker = Mturk.objects.get(Participant__code=participant_code)
    except ObjectDoesNotExist:
        return None

    mturker.current_wp = None
    mturker.save()
    print('somebody disconnected...')
    Group('group_{}'.format(group_pk)).discard(message.reply_channel)
    send_message(message, app_name,group_pk, gbat, index_in_pages)


def add_one(player, name_of_the_record):
    var = player.participant.vars.get(name_of_the_record, 0) + 1
    player.participant.vars[name_of_the_record] = var


