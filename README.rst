========================================================================
Custom Waiting Page for mTurk experiments with oTree
========================================================================

This project is a collaboration between Essi Kujansuu (EUI), Nicolas Gruyer (`Economics Games <https://economics-games.com>`_) and Philipp Chapkovski (UZH).


This code has been tested and seems to work fine with with oTree 1.4.2 and 2.1.9 (after adaptiong the code, if oTree 2). It has not been tested with other versions.

Note : Be careful, if you use the CustomMturkWaitPage in an elaborate experiment, with a sequence of several apps and/or a complex grouping logic. 
It can be used in these situations, but this is less easy and would probably require that you understand how the code of page works (how it sets exiters, how it allows exiters to go through "standard" pages...). Otherwise, I would advise you to not depart from standard uses (cf. examples that are provided). 
In particular, a CustomMturkWaitPage is an extension of a standard oTree Wait Page with "group_by_arrival_time = True", even if you do not declare it in your app. Consequently, it must only be used as the first page of the page_sequence of an app.

Installation:
***************
1. Download the project and copy the ``otree_mturk_utils`` folder into your project folder, next to your app folders. 

2. After that, add "otree_mturk_utils" to your INSTALLED_APPS section of ``settings.py`` file like this::

    INSTALLED_APPS = [
        'otree',
        'otree_mturk_utils',
    ]
You will also need to install radiogrid, which is used in one of the 2 tasks. Type ``pip install django-radiogrid`` in your terminal.

3. If you use oTree version 2, add "otree_mturk_utils" to your EXTENSION_APPS section of ``settings.py`` file like this::

    EXTENSION_APPS  = [
        'otree_mturk_utils',
    ].

You will also need to run the standard update process detailed in the `otree manual <https://otree.readthedocs.io/en/latest/misc/v20.html#updating-your-code>`_. If you want to run the 2 demo apps, you will also need to search for ``from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage`` in the pages/views files of the 2 apps and replace ``otree_mturk_utils.views`` with ``otree_mturk_utils.pages``.

4. In the ``views.py`` file of your project, import the pages::

    from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage 
(or ``from otree_mturk_utils.pages import CustomMturkPage, CustomMturkWaitPage`` if you use otree 2)

How to use it:
***************
The CustomMturkWaitPage is an extension of a standard oTree WaitPage with the setting ``group_by_arrival_time = True``. Consequently, it must necessarily be the first page of the page_sequence of an app. If you want to include a consent form before, you should put it in a first, separate app.

To include a CustomMturkWaitPage, just inherit your wait pages from CustomMturkWaitPage instead of the 'standard' oTree WaitPage::

      from otree_mturk_utils.views import CustomMturkPage, CustomMturkWaitPage

      class MyWaitPage(CustomMturkWaitPage):
           ...

Also inherit your other "non-wait pages" from CustomMturkPage instead of Page (this is necessary to allow a participant to reach the end of the module or the end of the experiment if he has waited too much).

Other standard wait pages, not located at the first position of the app, should be declared as a WaitPage, as usual.

The CustomMturkWaitPage has, in addition to standard properties of an oTree WaitPage (such as ``wait_for_all_groups`` or ``group_by_arrival_time``), six additional properties (see details in the section below):

1. ``pay_by_task``: compensation (in points or dollars) for each task correctly submitted at the waiting page. Default value: ``0`` (Note that for now this is only implemented for the real effort task survey: if you want to include pay by answer for the survey, you should adapt the wait pages).

2. ``pay_by_time``: compensation (in points or dollars) for each second of waiting at the waiting page. Default value: ``0``.

3. ``max_payment_for_the_page``: Maximum compensation (in points or dollars) for the page. Default value: ``None``.

4. ``startwp_timer``: After how long will the participant be offered to quit the study (in seconds). Default value: ``7200``.

5. ``task``: What kind of activity a person can do while waiting. Right now there are two options: filling in a 'Big Five' questionnaire and a real effort task (finding sum of two maximum numbers). In the future we will add games as an option (tic tac toe, snake, hangman etc.) . Possible values now: ``['survey', 'real_effort']``. Default value: ``real_effort`` . (Note: The 'survey' task might need to be adapted if you use oTree 2+, in order to remove radiogrid)'

6. ``use_task``: whether the participant will see any kind of tasks while waiting. Default value: ``True``.

7. ``skip_until_the_end_of`` : whether participants who ask to stop waiting, should skip the whole experiment or only the current app, or only the current round (also remember that participants will not skip pages that do not inherit from CustomMturkPage, whatever the value of this attribute. The will skip standard Wait Pages if they are located in the same app). Default value: ``experiment`` . Other possible values: ``app`` and ``round``. (Note, in case you have several apps in the sequence and want to allow a participant to skip everything until the end of the experiment: once you have included a CustomMturkWaitPage in an app, you might have to also add a CustomMturkWaitPage at the start of the following apps).


What does the default Custom MTurk Wait Page do?
******************************************
This custom wait page was created to allow participants to wait for a group to form,
to ensure that they remain available and ready to start the experiment while they wait,
and to let them finish part of, or the whole experiment if they have been waiting for too long.

The experimenter can require the participant to do an activity while he waits,
by setting two attributes of the page (here use_task = True and task = 'real_effort'
to have a real effort task). The main goal of this activity is to have the participant
stay focused on the experiment while he waits. But be careful, as soon as a group is formed,
the members of the group will be forwarded to the next page, even if they are in the middle of a page.
This could create frustration if not anticipated, so you should warn the participants in the instructions.
(If the task is to answer a survey, they will be offered to complete the survey at the end of the experiment,
their previous answers will be saved). Alternatively, you can change the javascript behavior of the page when a group is formed, but this is a bit more advanced (see the annex below).

You can decide to pay the participant based on his wait time and on his “score” in the effort
task by setting the attributes pay_by_task and pay_by_time in your waitpage (by default, this is 0). At the end of the experiment, you will find this additional payment in participant.vars[‘payment_for_wait’].

The experimenter can also set a limit of time after which a player is offered to exit the study
if he wants (by specifying the attribute “startwp_timer”, labelled in minutes, which is by default
equal to 2 hours). A timer will appear on the waitpage to indicate how much longer the participant must wait before being able to exit the experiment (hidden if more than 30 minutes are left). By clicking on “finish the study”, the participant will skip
all the CustomMturkPage and CustomMturkWaitPage pages in the rest of the round (if skip_until_the_end_of = 'round'), of the app (if skip_until_the_end_of = 'round'), or of the experiment (if skip_until_the_end_of = 'experiment'. In this case, just make sure that a CustomMturkWaitPage is also included at the start of each of the subsequent app that you want the participant to skip. Finally, if you want the participant to skip the whole experiment but to complete a survey in a final app, just do not inherit the survey pages from CustomMturkPage).

(Technical note: "exiters" will go through all "is_displayed" methods but will not enter "before_next_page" of the pages that are skipped, which is the standard oTree behavior on pages that return is_displayed = False. "Exiters" will go through standard wait pages, as a player in a "one-player group")

The CustomMturkWaitPage also displays the number of participants missing before a group can be formed (you might need to hide or adapt this if your grouping logic is complex).

You will find two examples in the project (testapp and testapp2). **You will probably find it easier if you take a little time to really understand the "testboth" example, and perhaps "play" around it, changing parameters and adding pages, to see what happens, before applying the pages to your project.**


Annex (more advanced): Transition at the end of the wait page, when groups are formed
*************************************************************************************

If you want to add your own behaviour to the custom wait page, for example, in order to "smooth" the exit of the page when a group is formed, you can replace all the content of the template GenericExtendedWaitPage.html, including the extension declaration at the top of it, with the complete content of the otree core original WaitPage.html template (the template that GenericExtendedWaitPage.html extends, by default). You can find that page in the ``\templates\otree`` folder of your otree-core folder.

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
    }, 10000);
    
instead of just ``window.location.href = '{{ view.redirect_url|safe }}';``





THIS CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
