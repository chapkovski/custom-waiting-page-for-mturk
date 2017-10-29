

        $(document).ready(function () {
            $(window).keydown(function (event) {
                if (event.keyCode == 13) {
                    event.preventDefault();
                    return false;
                }
            });
        });

        $("button.answer").on("click", function () {
            var $answer = $('input#answer');
            var msg = {
                'answer': $answer.val(),
            };
            if (wpsocket.readyState === wpsocket.OPEN) {

                wpsocket.send(JSON.stringify(msg));
            }
            ;
            $answer.val('');
        });

        $("input#answer").keyup(function (event) {
            if (event.keyCode == 13) {
                event.preventDefault();
                $("button.answer").click();
            }
        });

        // Handle messages sent by the server.
        wpsocket.onmessage = function (event) {

            var obj = JSON.parse(event.data);
            if (obj.hasOwnProperty('message_type')) {
                if (obj.message_type == 'new_task') {
                        $('span#correct_answer').html(obj.correct_answer);
                        $('span#tasks_attempted').html(obj.tasks_attempted);
                        $('span#tasks_correct').html(obj.tasks_correct);
                        $('table#box1').empty();
                        $('table#box2').empty();
                        $.each(obj.mat1, function (i, row) {
                            var tr = $('<tr>');
                            $.each(row, function (j, cell) {
                                $('<td>').html(cell).appendTo(tr);
                            });
                            $('table#box1').append(tr);
                        });
                        $.each(obj.mat2, function (i, row) {
                            var tr = $('<tr>');
                            $.each(row, function (j, cell) {
                                $('<td>').html(cell).appendTo(tr);
                            });
                            $('table#box2').append(tr);
                        });

                        var obj = jQuery.parseJSON(event.data);
                }
                else {
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
                    ;
                }
                ;

            }
            ;
        };
