from channels.routing import route
from customwp.consumers import ws_message, ws_connect, ws_disconnect
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
