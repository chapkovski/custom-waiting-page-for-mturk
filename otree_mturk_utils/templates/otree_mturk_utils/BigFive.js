

    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var big5socket = new WebSocket(ws_scheme + '://' + window.location.host + "/bigfive/{{participant.code}}");

    var old_answers;
    var anss;
    var i = 0;
    var participant_code = "{{ participant.code }}";

    $('input[name^="bigfive"]').on('click', function () {
        arr_to_send = {};
        $('input[name^="bigfive"]:checked').each(function (index, value) {
            arr_to_send[value.name.substring(8)] = value.value;
        });
        send_answers(arr_to_send);
    });


    send_answers = function (answers) {
        var msg = {
            participant_code: participant_code,
            answers: answers
        };
        if (big5socket.readyState === big5socket.OPEN) {
            big5socket.send(JSON.stringify(msg));
        }
    };


    window.onload = function () {
        i = 0;
        old_answers = {{old_data |safe}};
        console.log(old_answers);
        ;
        for (var ans = 0; ans < {{num_questions }}
        ;ans++
    )
        {
            anss = old_answers[ans] - 1;
            if (anss > -1) {
                $("input#id_bigfive_" + i + "_" + anss).prop("checked", true);
            }
            i += 1;
        }
    };



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





