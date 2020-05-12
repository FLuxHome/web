$(document).ready(function() {
    getPostsOnPage();
});


function getPostsOnPage() {
    var url = window.location.href.split("/");
    var id = url[url.length - 1];
    $.post("/get_posts/" + id, function(data) {
        $("#wallPosts").append(data);
        // Some FUNC $("#bday").html("html text")
   });
};


function createNewPost(wall_id, creator) {
    var text = "content=" + $('#post-text').val() + "&wall_posted=" + wall_id + "&creator=" + creator;
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var xhr = new XMLHttpRequest();

    if (text) {
        xhr.open("POST", '/new_post', true);
        xhr.setRequestHeader('Key', key);
        xhr.send(text);
        xhr.onreadystatechange = function() {
            if (this.readyState != 4) return;
                $("#wallPosts").before(this.responseText);
          }
    }
    $("#post-text").val("");
}


function addFriendRequest(initiator, recipient) {
    var following = `<div class="add-friend">
    <button class="btn btn-primary set-width" type="button" data-toggle="dropdown" id="add-friend">You're following
        <span class="caret"></span>
    </button>
</div>`;
    var key = "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14";
    var data = {"initator": initiator, "recipient": recipient, "key": key};
    $.post("/add_friend_request", data, function(data) {
        $("#follow").html(following);
    });
}


//$(document).ready(function() {
//    $("#btnSubmit").click(function(){
//        $.post("/postAction", {'text': "qwerty"}, function(data) {
//              alert("Data Loaded: " + data);
//        });            
//    });
//});

//$(document).ready(function() {
//    $("a#cash").on("click", function(e) {
//        console.log(e);
//      })
//    });


//function onClicked(element) {
//    $.post("/postAction", {"text": "qwerty"}, function(data) {
//        $("#bday").html('<div class="feed-header-font fl_l" id="bday">' + toString(this) + '</div>');
//    });
//}
