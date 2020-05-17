from flask import render_template, redirect, flash, url_for, request
from sqlalchemy.orm.exc import NoResultFound
from flask_login import current_user, login_required, login_user, logout_user
from Shreddit.wtforms import LoginForm, RegistrationForm, PostForm
from Shreddit.orm_forms import User, Post, Like, DisLike, Friend, Message, Comment
from Shreddit import db, bcrypt_flask, app
from datetime import datetime


@app.route("/home")
@app.route("/")
def home():
    if current_user.is_authenticated:
        posts_to_display = []
        all_posts = [friend.posts for friend in get_friends(current_user)]
        all_posts = all_posts + [current_user.posts]
        for post_container in all_posts:
            for post in post_container:
                posts_to_display.append(get_post(post, raw=True))
        posts_to_display.sort(key=lambda x: x["time_created"], reverse=True)
        return render_template("home.html", posts=posts_to_display)
    else:
        return render_template("new_user.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("home")
    form = LoginForm()
    if form.validate_on_submit():
        pw, email = form.password.data, form.email.data
        try:
            user = User.query.filter(User.email == email).one()
        except NoResultFound:
            flash("Something is wrong! Check password and username!", "alert alert-danger")
            return render_template("login.html", form=form)
        if bcrypt_flask.check_password_hash(user.password, pw):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("home"))
        else:
            flash("Something went wrong! Check password and username.", "alert alert-danger")
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("home")
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt_flask.generate_password_hash(form.password.data).decode("utf-8")
        name, surname, birthday = form.name.data, form.surname.data, form.birthday.data
        user = User(password=hashed_pw, email=form.email.data, name=name, surname=surname, birthday=birthday)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("registration.html", form=form)


@app.route("/profile")
@login_required
def profile():
    return redirect(url_for(f"true_profile", user_id=current_user.id))


@app.route("/profile/<user_id>", methods=["GET", "POST"])
@login_required
def true_profile(user_id):
    form = PostForm()
    try:
        user = User.query.filter_by(id=user_id).one()
        is_following, is_friend = check_comms(user)
    except NoResultFound:
        return redirect(f"profile/{current_user.id}")
    print(is_following, is_friend)
    is_current_user = user == current_user
    args = {"is_current_user": is_current_user, "user": user, "is_friends": is_friend,
            "current_user": current_user, "is_following": is_following}

    return render_template("profile.html", args=args, form=form)


@app.route("/friends")
@login_required
def friends_redirect():
    return redirect(url_for("friends", user_id=current_user.id))


@app.route("/friends/<user_id>")
@login_required
def friends(user_id):
    if int(user_id) != current_user.id:
        return redirect(url_for("friends", user_id=current_user.id))
    try:
        user = User.query.filter_by(id=user_id).one()
    except NoResultFound:
        return redirect(url_for("friends", user_id=current_user.id))
    friend_list, follow_list = get_all_friends(user)
    return render_template("friends.html", friend_list=friend_list, follow_list=follow_list)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/get_posts/<user_id>", methods=["POST"])
def get_posts(user_id):
    if not user_id.isdigit():
        return
    string = ""
    if user_id is None:
        user_id = current_user.id
    posts = Post.query.filter_by(wall_posted=user_id).all()
    posts.sort(key=lambda x: x.date_posted)
    for i, post in enumerate(posts[::-1]):
        string += get_post(post)
    return string


@app.route("/update_post", methods=["POST"])
def update_post():
    ans = request.get_data().decode("UTF-8")
    ans = list(item.split("=")[1] for item in ans.split("&"))
    like_handler(int(ans[0]), int(ans[1]), int(ans[2]), ans[3])
    post = Post.query.filter_by(id=int(ans[0])).one()
    return get_post(post, single=True)


@app.route("/new_comment", methods=["POST"])
def create_comment():
    ans = request.get_data().decode("UTF-8")
    comment, post_id, user_id = list(item.split("=")[1] for item in ans.split("&"))
    new_comment = Comment(content=comment, post_id=post_id, posted_by=user_id)

    db.session.add(new_comment)
    db.session.commit()

    print(ans)

    return ""


@app.route("/update_comment", methods=["POST"])
def update_comment():
    ans = request.get_data().decode("UTF-8")
    comment_id, user_id, action, key = list(item.split("=")[1] for item in ans.split("&"))
    comment_id, user_id, action = int(comment_id), int(user_id), int(action)
    comment = Comment.query.filter_by(id=comment_id).one()
    if action == 1 and user_id in [item.liked_by for item in comment.likes]:
        like = Like.query.filter_by(liked_by=user_id, comment_id=comment_id).one()
        db.session.delete(like)
    elif action == 2 and user_id in [item.disliked_by for item in comment.dislikes]:
        dislike = DisLike.query.filter_by(disliked_by=user_id, comment_id=comment_id).one()
        db.session.delete(dislike)
    elif action == 1:
        like = Like(liked_by=user_id, comment_id=comment_id, post_id=None)
        db.session.add(like)
    elif action == 2:
        dislike = DisLike(disliked_by=user_id, comment_id=comment_id, post_id=None)
        db.session.add(dislike)

    db.session.commit()

    return ""


@app.route("/new_post", methods=["POST"])
def create_new_post():
    ans = request.get_data().decode("UTF-8")
    print(ans)
    val, wall_posted, creator = list(item.split("=")[1] for item in ans.split("&"))
    key = request.headers["Key"]
    if not key or \
            key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    post = Post(posted_by=creator, content=val, date_posted=datetime.now(), wall_posted=wall_posted)
    db.session.add(post)
    db.session.commit()
    return get_post(current_user.posts[-1])


@app.route("/add_friend_request", methods=["POST"])
def add_friend_request():
    ans = request.get_data().decode("UTF-8")
    initiator, recepient, key = list(item.split("=")[1] for item in ans.split("&"))

    if not key or \
            key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    friend = Friend(initiator=initiator, recepient=recepient, pending=True)
    db.session.add(friend)
    db.session.commit()

    return ""


@app.route("/add_friend", methods=["POST"])
def add_friend():
    ans = request.get_data().decode("UTF-8")
    initiator, recepient, key = list(item.split("=")[1] for item in ans.split("&"))

    if not key or \
            key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    try:
        friend_obj = Friend.query.filter_by(recepient=recepient, initiator=initiator).one()
    except NoResultFound:
        friend_obj = Friend.query.filter_by(recepient=initiator, initiator=recepient).one()

    friend_obj.pending = False
    db.session.commit()

    return ""


@app.route("/remove_friend", methods=["POST"])
def remove_friend():
    ans = request.get_data().decode("UTF-8")
    initiator, recepient, key = list(item.split("=")[1] for item in ans.split("&"))

    if not key or \
            key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    try:
        friend_obj = Friend.query.filter_by(recepient=recepient, initiator=initiator).one()
    except NoResultFound:
        friend_obj = Friend.query.filter_by(recepient=initiator, initiator=recepient).one()

    db.session.delete(friend_obj)
    db.session.commit()

    return ""


@app.route("/messages")
@login_required
def messages():
    friend_list = get_friends(current_user)

    print(friend_list)

    return render_template("messages_list.html", friends=friend_list)


@app.route("/chat/<user_id>")
@login_required
def chat(user_id):
    partner = User.query.filter_by(id=user_id).one()
    message_list = create_message_list(user_id)

    return render_template("messages.html", user=partner, message_list=message_list)


@app.route("/send_message", methods=["POST"])
def send_message():
    key = request.headers["Key"]
    ans = request.get_data().decode("UTF-8")

    if not key or \
            key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    content, initiator, recepient = list(item.split("=")[1] for item in ans.split("&"))

    message = Message(content=content, initiator=initiator, recepient=recepient, date=datetime.now())

    db.session.add(message)
    db.session.commit()

    partner = User.query.filter_by(id=recepient).one()
    message_list = create_message_list(recepient)
    return render_template("message_content_sample.html", message_list=message_list, user=partner)


@app.route("/get_comments", methods=["POST"])
def get_comments():
    ans = request.get_data().decode("UTF-8")
    post_id = [item.split("=")[1] for item in ans.split("&")][0]
    comment_data = []
    post = Post.query.filter_by(id=int(post_id)).one()
    for comment in post.comments:
        user = User.query.filter_by(id=comment.posted_by).one()
        name = user.name + ' ' + user.surname
        comment_data.append({"id": comment.id, "name": name, "body": comment.content,
                             "likes_amount": len(comment.likes), "dislikes_amount": len(comment.dislikes)})

    return render_template("comments.html", comments=comment_data, post_id=post_id)


def get_post(post, single=False, raw=False):
    posted_by = User.query.filter_by(id=post.posted_by).one()

    if current_user.id in [item.liked_by for item in post.likes]:
        color_up = "red"
    else:
        color_up = "black"
    if current_user.id in [item.disliked_by for item in post.dislikes]:
        color_down = "blue"
    else:
        color_down = "black"

    post = {"name": posted_by.name + " " + posted_by.surname, "content": post.content, "id": post.id,
            "user_id": posted_by.id, "likes_amount": len(post.likes),
            "comments_amount": len(post.comments), "dislikes_amount": len(post.dislikes),
            "color_up": color_up, "color_down": color_down, "time_created": post.date_posted}
    if raw:
        return post
    return render_template("post_sample.html", post=post) if not single else \
        render_template("single_post_sample.html", post=post)


def like_handler(post_id, user_id, action, key):
    container = False, -1, DisLike if action == 1 else Like

    if key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    for like in current_user.likes:
        if like.post_id == post_id and action == 1:
            delete_record(like.id, Like)
            return
        if like.post_id == post_id and action == 2:
            container = True, like.id, Like
            break

    for dislike in current_user.dislikes:
        if container[0]:
            break
        if dislike.post_id == post_id and action == 2:
            delete_record(dislike.id, DisLike)
            return
        if dislike.post_id == post_id and action == 1:
            container = True, dislike.id, DisLike

    if container[0]:
        db.session.query(container[2]).filter_by(id=container[1]).delete()

    if container[2].__name__ == "DisLike":
        obj = Like(liked_by=user_id, post_id=post_id, comment_id=None)
    else:
        obj = DisLike(disliked_by=user_id, post_id=post_id, comment_id=None)
    db.session.add(obj)
    db.session.commit()


def comment_like_handler(comment_id, user_id, action, key):
    if key != "879858348c418a0b743175365355f403f12e7655d9534c03a13ccb3e85043b14":
        return

    comment = Comment.query.filter_by(id=comment_id).one()
    print(comment.likes)

def check_comms(user):
    is_following, is_friends = False, False

    for item in current_user.friends_i:
        if item.recepient == user.id and item.pending:
            return True, False
        elif item.recepient == user.id and not item.pending:
            return False, True

    for item in current_user.friends_r:
        if item.initiator == user.id and item.pending:
            return True, False
        elif item.initiator == user.id and not item.pending:
            return False, True

    return is_following, is_friends


def get_all_friends(user):
    friend_list = []
    follow_list = []
    user_list = user.friends_i + user.friends_r

    for item in user_list:
        user_i = User.query.filter_by(id=item.initiator).one()
        user_r = User.query.filter_by(id=item.recepient).one()
        if user_r.id == current_user.id and item.pending:
            follow_list.append({"user": user_i, "is_friends": False, "is_following": True})
        elif user_r.id == current_user.id:
            friend_list.append({"user": user_i, "is_friends": True, "is_following": False})
        elif user_i.id == current_user.id and not item.pending:
            friend_list.append({"user": user_r, "is_friends": True, "is_following": False})

    return friend_list, follow_list


def get_friends(user):
    friends_list = [item.initiator for item in current_user.friends_r
            if item.initiator != current_user.id and not item.pending] + \
             [item.recepient for item in current_user.friends_i
              if item.recepient != current_user.id and not item.pending]
    friends_list = [User.query.filter_by(id=i).one() for i in friends_list]
    return friends_list


def delete_record(id_obj, obj):
    db.session.query(obj).filter_by(id=id_obj).delete()
    db.session.commit()


def create_message_list(user_id):
    partner = User.query.filter_by(id=user_id).one()
    user_id = int(user_id)
    partner_messages = [message for message in partner.messages
                        if message.initiator == user_id and message.recepient == current_user.id]
    user_messages = [message for message in current_user.messages
                     if message.initiator == current_user.id and message.recepient == user_id]
    message_list = partner_messages + user_messages
    message_list.sort(key=lambda x: x.date, reverse=True)

    return message_list
