import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError
from config import User

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


@app.route("/")
@login_required
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
