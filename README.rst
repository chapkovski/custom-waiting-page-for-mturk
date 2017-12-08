========================================================================
Custom waiting page for mTurk experiments with oTree
========================================================================

This project is a collaboration between Essi Kujansuu (EUI), Nicolas Gruyer (`Economics Games <https://economics-games.com>`_) and Philipp Chapkovski (UZH).

Installation:
***************
1. **Either**:

- type ``pip install mturkotreeutils`` in your terminal window.


2. **or**:

-  clone exisiting project ``git clone https://github.com/chapkovski/custom-waiting-page-for-mturk`` and copy the ``otree_mturk_utils`` folder into your project folder, next to the apps of your module.

3. After that add "otree_mturk_utils" to your INSTALLED_APPS section of ``settings.py`` file like this::

    INSTALLED_APPS = [
        'otree',
        'otree_mturk_utils',
    ]

4. In the ``views.py`` file of your project, import the pages::

    from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage

How to use it:
***************
To use the custom waiting page, just inherit your WaitPage not from the 'standard' oTree WaitPage, but from CustomMturkWaitPage::

      from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage

      class MyWaitPage(CustomMturkWaitPage):
           ...

the CustomMturkWaitPage has in addition to standard properties of oTree WaitPage (such as ``wait_for_all_groups`` or ``group_by_arrival_time``), four additional properties (see details in the section below):

1. ``pay_by_task``: compensation (in points or dollars) for each task correctly submitted at the waiting page. Default value: ``0``.

2. ``pay_by_time``: compensation (in points or dollars) for each minute of waiting at the waiting page. Default value: ``0``.

3. ``startwp_timer``: How fast the participant can quit the study (in seconds). Default value: ``Never``.

4. ``task``: What kind of activity a person can do while waiting. Right now there are two options: filling in a 'Big Five' questionnaire and a real effort task (finding sum of two maximum numbers). In the future we will add games as an option (tic tac toe, snake, hangman etc.) . Possible values now: ``['survey', 'real_effort']``. Default value: ``real_effort`` .

5. ``use_task``: whether the participant will see any kind of tasks while waiting. Default value: ``True``.

6. ``skip_until_the_end_of`` : whether participants who ask to stop waiting, should skip the whole experiment or only the current app, or only the current round (also remember that participants will not skip pages that do not inherit from CustomMturkPage, CustomMturkWaitPage, whatever this attribute is). Default value: ``experiment`` . Other possible values: ``app`` and ``round``.

What does the default custom wait page do?
******************************************

The custom wait page was created to allow participants to wait for a group to form,
to ensure that they remain available and ready to start the experiment while they wait,
and to let them finish the experiment if the waiting lasts for too long.

The experimenter can require the participant to do an activity while he waits,
by setting an attribute of the page (here use_real_effort_task = True ,
to have a real effort task). The main goal of this activity is to have the participant
stay focused on the experiment while he waits. But be careful, as soon as a group is formed,
the members of the group will be forwarded to the next page, even if they are in the middle of a page.
This could create frustration if not anticipated, so you should warn the participants in the instructions.
(If the task is to answer a survey, they will be offered to complete the survey at the end of the experiment,
their previous answers will be saved). Alternatively, you can change the javascript behavior of the page when a group is formed, but this is a bit more advanced (see the annex below)

You can decide to pay the participant based on his wait time and on his “score” in the effort
task by setting the attributes pay_by_task and pay_by_time in your waitpage (by default, this is 0). At the end of the experiment, you will find this additional payment in participants.vars[‘payment_for_wait’]

The experimenter can also set a limit of time after which a player is offered to complete the study
if he wants (by specifying the attribute “time_before_exit_offer”, labelled in minutes, which is by default
equal to 2 hours). This is hidden if more than 30 minutes. By clicking on “finish the study”, the participant will skip
all the CustomMturkPage and CustomMturkWaitPage pages in the remaining app sequence (if you want him to complete a survey
in a final app, just do not inherit the survey pages from CustomMturkPage).

Maybe in a later version, we might offer a feature detecting if the remaining participants are not enough for creating
a new group, to signal the waiting participants that it is not necessary to wait.


Annex: Transition at the end of the wait page, when groups are formed
*********************************************************************

If you want to add your own behaviour to the custom wait page, for example, in order to "smooth" the exit of the page when a group is formed, you can replace all the content of the template GenericExtendedWaitPage.html, including the extension declaration at the top of it, with the complete content of the otree core original WaitPage.html template (the template that GenericExtendedWaitPage.html extends, by default).

For now, you can find that otree-core version, for the last version, at this address: https://github.com/oTree-org/otree-core/blob/master/otree/templates/otree/WaitPage.html .

Then you can add your own content inside, for example in the socket.onmessage part, if you want something special to happen when the page receives the signal that a group has been formed.

Be careful, the WaitPage in otree-core can change from an oTree version to another: If you update otree core, you might need to adapt GenericExtendedWaitPage.html, with the content of the new otree-core WaitPage.html.

You will find an example, in GenericExtendedWaitPageExample1ForOTree140.html, that is based on the WaitPage of oTree-core 140. This is just a quick and dirty extension, that only shows an ugly alert box, in order to warn the participant that he will be forwarded to the next page, when the group is matched (we just added: "alert('Enough persons have arrived, you will be transfered to the next page; You will be invited to finish your study at the end of the experiment');")

In the second example, GenericExtendedWaitPageExample2ForOTree140.html, a hidden message is shown via
::
    <div class="well" id="show-when-group-is-formed" style="display:none; color:red;">
        <b>Enough persons have arrived, you will be transfered to the next page; 
        You will be invited to finish your study at the end of the experiment.</b>
    </div>

and
::
    $("#show-when-group-is-formed").show();

and the redirection is delayed by 10s (10 000 ms):
::
    window.setInterval(function() {
        window.location.href = '{{ view.redirect_url|safe }}';
    }, 10000);``
    
instead of just ``window.location.href = '{{ view.redirect_url|safe }}';``