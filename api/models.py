from api.exts import db


# 用户表
class User(db.Model):
    __tablename__ = 'user'
    openid = db.Column(db.String(30), primary_key=True, unique=True)
    register = db.Column(db.DateTime)
    latest = db.Column(db.DateTime)
    count = db.Column(db.Integer)

# 问卷表
class Questionaire(db.Model):
    __tablename__ = 'questionaire'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    openid = db.Column(db.String(30))
    data = db.Column(db.Text)
