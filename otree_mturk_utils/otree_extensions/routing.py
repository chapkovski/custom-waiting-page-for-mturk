from channels.routing import route
from otree_mturk_utils.consumers import ws_message, ws_connect, ws_disconnect, big_connect, big_message, big_disconnect
from otree.channels.routing import channel_routing
from channels.routing import include, route_class
waiting_channel_name = r'^/(?P<participant_code>\w+)/(?P<app_name>\w+)/(?P<group_pk>\w+)/(?P<player_pk>\w+)/(?P<index_in_pages>\w+)/(?P<gbat>\w+)$'
customwp_routing = [route("websocket.connect",
                 ws_connect,  path=waiting_channel_name ),
                 route("websocket.receive",
                       ws_message,  path=waiting_channel_name ),
                 route("websocket.disconnect",
                       ws_disconnect,  path=waiting_channel_name ), ]
channel_routing += [
    include(customwp_routing, path=r"^/waiting_page"),
]

bigfive_path = r'^/(?P<participant_code>\w+)$'
bigfive_routing = [route("websocket.connect", big_connect, path=bigfive_path),
                   route("websocket.receive", big_message, path=bigfive_path),
                   route("websocket.disconnect", big_disconnect, path=bigfive_path) ]

channel_routing += [
    include(bigfive_routing, path=r"^/bigfive"),
]
