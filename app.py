import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from config import User, Message

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Flaskでsessionを使う場合に必要
login_manager = LoginManager()
login_manager.init_app(app)


# Flask-Loginがユーザー情報を取得するためのメソッド
@login_manager.user_loader
def load_user(user_id):
    return User.get(id=int(user_id))


# ログインしていないとアクセスできないページにアクセスがあった場合の処理
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for("login"))


# ユーザー登録フォームの表示・登録処理
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST" and request.form["name"] and request.form["password"] and request.form["email"]:
        if User.select().where(User.name == request.form["name"]).first():
            flash("その名前はすでに使われています")
            return redirect(request.url)

        if User.select().where(User.email == request.form["email"]).first():
            flash("そのメールアドレスはすでに使われています")
            return redirect(request.url)
        try:
            user = User.create(
                name=request.form["name"],
                email=request.form["email"],
                password=generate_password_hash(request.form["password"]),
            )
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))
        except IntegrityError:
            flash("登録に失敗しました")
    return render_template("register.html")


# ログインフォームの表示・ログイン処理
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and request.form["email"] and request.form["password"]:
        user = User.select().where(User.email == request.form["email"]).first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))
        else:
            flash("認証に失敗しました")
    return render_template("login.html")


# ログアウト処理
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました！")
    return redirect(url_for("index"))


# @app.route("/")
# @login_required
# 一覧表示・新規登録
@app.route("/", methods=["GET", "POST"])
def index():
    # return render_template("index.html")
    if request.method == "POST" and current_user.is_authenticated:
        Message.create(user=current_user, content=request.form["content"])
    messages = (
        Message.select().where(Message.reply_to.is_null(True)).order_by(Message.pub_date.desc(), Message.id.desc())
    )
    return render_template("index.html", messages=messages)


# メッセージ削除
@app.route("/messages/<message_id>/delete/", methods=["POST"])
@login_required
def delete(message_id):
    if Message.select().where((Message.id == message_id) & (Message.user == current_user)).first():
        Message.delete_by_id(message_id)
    else:
        flash("無効な操作です")
    return redirect(url_for("index"))


# 返信登録
@app.route("/messages/<message_id>/", methods=["POST"])
@login_required
def reply(message_id):
    Message.create(user=current_user, content=request.form["content"], reply_to=message_id)
    return redirect(url_for("show", message_id=message_id))


# 返信表示
@app.route("/messages/<message_id>/")
def show(message_id):
    messages = (
        Message.select()
        .where((Message.id == message_id) | (Message.reply_to == message_id))
        .order_by(Message.pub_date.desc(), Message.id.desc())
    )
    return render_template("show.html", messages=messages, message_id=message_id)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
