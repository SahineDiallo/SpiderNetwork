$(document).ready(function () {

    function scrollSmoothToBottom(id) {
        var div = document.getElementById(id);
        if (div !== null) {

            $('#' + id).animate({
                scrollTop: div.scrollHeight - div.clientHeight
            }, 300);
        }
    }
    scrollSmoothToBottom("messages-container");

    let _id;
    let _username
    var _id_ = document.getElementById("other_user_id")
    if (_id_ !== null) {
        _id = _id_.textContent
    }
    var _username_ = document.getElementById("current_user_username")
    if (_username_ !== null) {
        _username = _username_.textContent
    }
    var url = `ws://${window.location.host}/ws/personalChat/${_id}/`
    if (window.location.pathname.includes("chat")) {
        var socket = new WebSocket(url)
        $(".not-box-openm .notification.badge").fadeOut();
        socket.onopen = (event) => {
            console.log("CONNECTION OPEN")
        }
        socket.onmessage = (e) => {
            let data = JSON.parse(e.data)
            // here I need to send the data to the message area

            if (data.username !== _username) {
                console.log("the equal usernames")
                console.log(window.location.pathname)
            }
            let float = data.username !== _username ? "ta-right" : "st3"
            let st3 = float === "st3" ? "st3" : ""
            var msg_div = `
                <div class="main-message-box ${float}">
                    <div class="message-dt ${st3}">
                        <div class="message-inner-dt">
                            <p>${data.message}.</p>
                        </div>
                        <span>5 minutes ago</span>
                    </div>
                    <div class="messg-usr-img">
                        <img src="${data.avatar_url}" alt="">
                    </div>
                </div>
             `
            $(".messages-line").append(msg_div);
            scrollSmoothToBottom("messages-container");
        }
        socket.onerror = (e) => {
            console.log("there is an error", e)
        }
        socket.onclose = (event) => {
            console.log("CONNECTION CLOSE");
        }
        // update the timestamp of the userchant.
        setInterval(function () {
            socket.send(JSON.stringify("heartbeat"));
        }, 30000);

        var input_message = document.getElementById("send_message")
        if (input_message !== null) {
            input_message.addEventListener('click', (e) => {
                e.preventDefault();
                var message = $("#message_to_send").val();
                socket.send(JSON.stringify({
                    'message': message,
                    'username': _username,
                }));
                $("#message_to_send").val(" ")
            });
        }
    }

    var postLikeOrCommentUrl = `ws://${window.location.host}/ws/post-likeOrComment-notification/`
    postLikeOrCommentWebsocket = new WebSocket(postLikeOrCommentUrl);

    postLikeOrCommentWebsocket.onopen = (event) => {
        console.log("The nofify post like or comment websocket is CONNECTED");
    }
    postLikeOrCommentWebsocket.onclose = (event) => {

        console.log("The nofify post comment or like websocket is DISCONNECTED");
    }
    postLikeOrCommentWebsocket.onmessage = (event) => {
        data = JSON.parse(event.data)
        var [notif_div, num_of_notifs, notifs_badge] = data.notif_type !== 6 ? [
            $("#notification .nott-list"),
            $(".not-box-open .notification.badge").text(),
            $(".not-box-open .notification.badge")
        ] : [
            $("#message .nott-list"),
            $(".not-box-openm .notification.badge").text(),
            $(".not-box-openm .notification.badge")
        ]
        var notif_details = `
            <a href="/social/user-profile/${data.profile_slug}/">
                <div class="notfication-details">
                    <div class="noty-user-img">
                        <img src="${data.avatar_url}" alt="">
                    </div>
                    <div class="notification-info">
                        <h3>
                            <a href="/social/user-profile/${data.profile_slug}/" title="">${data.author}</a> 
                            ${data.message}.
                        </h3>
                        <span style="bottom: -13px;">${data.date_notif}</span>
                    </div>
                
                </div> 
            </a>           
        `
        UpdateNotificationUI(notif_details, notif_div, notifs_badge, num_of_notifs)
    }
    postLikeOrCommentWebsocket.onerror = (event) => {
        console.log(event);
    }


    function UpdateNotificationUI(notif_details_node, notifDiv, notif_badge, num_of_notif) {
        if (!(notif_badge.length)) {
            console.log("there is no pending notification for now.")
            var badge_span = `
            <span class="notification badge badge-danger">1</span>
            `
            // need to clear the first child of the notif list
            $(notifDiv).find(".no-notif").fadeOut("slow");
            $(".not-box-open").append(badge_span);
        } else {
            ("there are some notification in the badge")
            $(notif_badge).text(parseInt(num_of_notif) + 1)
        }
        $(notifDiv).prepend(notif_details_node)
    }

    var followersUrl = `ws://${window.location.host}/ws/user-followers-notification/`
    followersWebsocket = new WebSocket(followersUrl);

    followersWebsocket.onopen = (event) => {
        console.log("The nofify followers websocket is CONNECTED");
    }
    followersWebsocket.onclose = (event) => {
        console.log("The nofify followers websocket is DISCONNECTED");
    }
    followersWebsocket.onmessage = (event) => {
        // grap the notification div
        notifDiv = $("#notification .nott-list")
        data = JSON.parse(event.data)
        var notif_details = `
        <div class="notfication-details">
            <div class="noty-user-img">
                <img src="${data.avatar_url}" alt="">
            </div>
            <div class="notification-info">
            <h3>
                <a href="#" title="">${data.author}</a> 
                ${data.message}.
            </h3>
            <span>${data.date_sent}</span>
            </div>
        </div>
        `
        $(notifDiv).prepend(notif_details)
        console.log(data);
    }
    followersWebsocket.onerror = (event) => {
        console.log(event);
        console.log("The nofify followers websocket fall into an error");
    }
    setInterval(() => {
        $.ajax({
            url: "/connection/prune_presence/",
            method: "get",
            success: () => {
                //I will just ahve to check if the function works correctly
                // nothing else
            },
            error: (error) => {
                // check if there is any error encountered
            }
        })
    }, 30000)
})
