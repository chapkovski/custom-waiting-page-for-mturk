// Handle messages sent by the server.
wpsocket.onmessage = function (event) {

    var obj = JSON.parse(event.data);

    if (obj.hasOwnProperty('left_to_wait')) {
        left_to_wait = obj.left_to_wait;
        how_many_arrived = obj.how_many_arrived;
        $('#left_to_wait').html(left_to_wait);
        var people = left_to_wait != 1 ? 'participants' : 'participant'
        $('#left_to_wait_people').html(people);
        $('#how_many_arrived').html(how_many_arrived);
        people = how_many_arrived != 1 ? 's are' : ' is'
        $('#how_many_arrived_people').html(people);
    }
};
