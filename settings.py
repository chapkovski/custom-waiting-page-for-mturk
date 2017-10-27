import os
from os import environ

import dj_database_url
from boto.mturk import qualification


import otree.settings
# CHANNEL_ROUTING = 'customwp.routing.channel_routing'
# settings.py
# ROOT_URLCONF = 'urls'
# CHANNEL_ROUTING = 'pggfg.routing.channel_routing'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# the environment variable OTREE_PRODUCTION controls whether Django runs in
# DEBUG mode. If OTREE_PRODUCTION==1, then DEBUG=False
if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True

# don't share this with anybody.
SECRET_KEY = 'l&3%$it4n+o-cdwopdtra=hm96a)7ee2s@i4v_*638q4d)==t4'

# To use a database other than sqlite,
# set the DATABASE_URL environment variable.
# Examples:
# postgres://USER:PASSWORD@HOST:PORT/NAME
# mysql://USER:PASSWORD@HOST:PORT/NAME

DATABASES = {
    'default': dj_database_url.config(
        # default='postgres://otree_user:basset@localhost/django_db'
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    )
}

# AUTH_LEVEL:
# this setting controls which parts of your site are freely accessible,
# and which are password protected:
# - If it's not set (the default), then the whole site is freely accessible.
# - If you are launching a study and want visitors to only be able to
#   play your app if you provided them with a start link, set it to STUDY.
# - If you would like to put your site online in public demo mode where
#   anybody can play a demo version of your game, but not access the rest
#   of the admin interface, set it to DEMO.

# for flexibility, you can set it in the environment variable OTREE_AUTH_LEVEL
AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')


# setting for integration with AWS Mturk
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')


# e.g. EUR, CAD, GBP, CHF, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_DECIMAL_PLACES = 0
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 3

# e.g. en, de, fr, it, ja, zh-hans
# see: https://docs.djangoproject.com/en/1.9/topics/i18n/#term-language-code
LANGUAGE_CODE = 'en'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree', 'customwp']

# SENTRY_DSN = ''
# SENTRY_DSN = 'http://2d6137799b914e1693146c5011f39030:46838e8caa374937a91b14b59ebbe164@sentry.otree.org/36'

DEMO_PAGE_INTRO_TEXT = """
<ul>
    <li>
        <a href="https://github.com/oTree-org/otree" target="_blank">
            oTree on GitHub
        </a>.
    </li>
    <li>
        <a href="http://www.otree.org/" target="_blank">
            oTree homepage
        </a>.
    </li>
</ul>
<p>
    Here are various games implemented with oTree. These games are all open
    source, and you can modify them as you wish.
</p>
"""

ROOMS = [
    # {
    #     'name': 'econ101',
    #     'display_name': 'Econ 101 class',
    #     'participant_label_file': '_rooms/econ101.txt',
    # },

]


# from here on are qualifications requirements for workers
# see description for requirements on Amazon Mechanical Turk website:
# http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html
# and also in docs for boto:
# https://boto.readthedocs.org/en/latest/ref/mturk.html?highlight=mturk#module-boto.mturk.qualification

mturk_hit_settings = {
    'keywords': ['easy', 'bonus', 'choice', 'study'],
    'title': 'Title for your experiment',
    'description': 'Description for your experiment',
    'frame_height': 800,
    'preview_template': 'global/MTurkPreview.html',
    'minutes_allotted_per_assignment': 260,
    'expiration_hours': 7*24, # 7 days
    #'grant_qualification_id': 'YOUR_QUALIFICATION_ID_HERE',# to prevent retakes
    'qualification_requirements': [
        qualification.LocaleRequirement("EqualTo", "US"),
        # qualification.PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", 50),
        # qualification.NumberHitsApprovedRequirement("GreaterThanOrEqualTo", 5),
        # qualification.Requirement('YOUR_QUALIFICATION_ID_HERE', 'DoesNotExist')
    ]
}


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 0.001,
    'participation_fee': 0.50,
    'doc': "",
    'mturk_hit_settings': mturk_hit_settings,
}

# from colsan.models.Constants import players_per_group
SESSION_CONFIGS = [

    #
    {
        'name': 'customwp',
        'display_name': "Testing timeout on waiting page",
        'num_demo_participants': 3,
        'app_sequence': ['customwp'],
    },


]

# anything you put after the below line will override
# oTree's default settings. Use with caution.
# TEMPLATES = [{
#     'BACKEND': 'django.template.backends.django.DjangoTemplates',
#     'DIRS': [os.path.join(BASE_DIR, 'templates')],
# }]
# print(TEMPLATES)
otree.settings.augment_settings(globals())
# CHANNEL_LAYERS['inmemory']['BACKEND'] = 'otree.channels.asgi_redis.RedisChannelLayer'
