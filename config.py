import os
import datetime
import logging
from dotenv import load_dotenv
from playhouse.db_url import connect
from peewee import Model, IntegerField, CharField, TextField, TimestampField, ForeignKeyField
from flask_login import UserMixin

load_dotenv()

# 実行したSQLをログで出力する設定
logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = connect(os.environ.get("DATABASE", "sqlite:///db.sqlite"))

if not db.connect():
    print("接続NG")
    exit()


class User(UserMixin, Model):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True)
    email = CharField(unique=True)
    password = TextField()
    join_date = TimestampField(default=datetime.datetime.now)

    class Meta:
        database = db
        table_name = "users"


# db.create_tables([User])
class Message(Model):
    id = IntegerField(primary_key=True)
    user = ForeignKeyField(User, backref="messages")
    content = TextField()
    pub_date = TimestampField(default=datetime.datetime.now)
    reply_to = ForeignKeyField("self", backref="messages", null=True)  # nullを許容する

    class Meta:
        database = db
        table_name = "messages"


db.create_tables([User, Message])
