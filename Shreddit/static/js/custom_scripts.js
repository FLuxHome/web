function mouseOnBar(element) {
    element.style.background = "#DCDCDC";
}

function mouseOffBar(element) {
    element.style.background = "#F5F5F5";
}


function downArrowClicked(post_id, user_id, action) {
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14"
    var requset_body = {"post_id": post_id, "user_id": user_id, "action": action, "key": key}
    $.post("/update_post", requset_body, function(data) {
        $("#id_" + post_id).html(data);
        // Some FUNC $("#bday").html("html text")
    });
}


function upArrowClicked(post_id, user_id, action) {
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var requset_body = {"post_id": post_id, "user_id": user_id, "action": action, "key": key};
    $.post("/update_post", requset_body, function(data) {
        $("#id_" + post_id).html(data);
        // Some FUNC $("#bday").html("html text")
    });
}


function addFriend(recepient, iniciator) {
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var body = {"iniciator": iniciator, "recepient": recepient, "key":key};
    $.post("/add_friend", body);
}


function removeFriend(recepient, iniciator) {
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var body = {"iniciator": iniciator, "recepient": recepient, "key":key};
    $.post("/remove_friend", body);
}


function sendMessage(iniciator, recepient) {
    var text = "content=" + $('#messagearea').val() + "&iniciator=" + iniciator + "&recepient=" + recepient;
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var xhr = new XMLHttpRequest();

    if (text) {
        xhr.open("POST", '/send_message', true);
        xhr.setRequestHeader('Key', key);
        xhr.send(text);
        xhr.onreadystatechange = function() {
            if (this.readyState != 4) return;
                $("#messagearea").val("");
                $("#message-column").html(this.responseText);
          }
    }
}


function getComments(post_id) {
    body = "post_id=" + post_id;
    $.post("/get_comments", body, function(data) {
        $("#id_" + post_id).html($("#id_" + post_id).html() + data);
    })
}

function downArrowCommentClicked(comment_id, user_id, action) {
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14"
    var requset_body = {"comment_id": comment_id, "user_id": user_id, "action": action, "key": key}
    $.post("/update_comment", requset_body, function(data) {
    });
}


function upArrowCommentClicked(comment_id, user_id, action) {
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var requset_body = {"comment_id": comment_id, "user_id": user_id, "action": action, "key": key};
    $.post("/update_comment", requset_body, function(data) {
    });
}

function createNewComment(post_id, user_id) {
    var text = "content=" + $('#textAreaComments').val() + "&post=" + post_id + "&creator=" + user_id;
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var xhr = new XMLHttpRequest();

    if (text) {
        xhr.open("POST", '/new_comment', true);
        xhr.setRequestHeader('Key', key);
        xhr.send(text);
        xhr.onreadystatechange = function() {
            if (this.readyState != 4) return;
                // $("#wallPosts").before(this.responseText);
          }
    }
    $("#textAreaComments").val("");
};
