# coding=utf8
from flask import Flask, request, render_template, send_file, current_app, send_from_directory
import requests
import base64
import os
import time
import json
from flask_mail import Mail, Message
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
import api.configs as configs
from api.exts import db
from api import models
from loguru import logger
import threading


app = Flask(__name__)

app.config.from_object(configs)

db.init_app(app)

app.config['SECRET_KEY'] = 'samueli924'

app.config['MAIL_SERVER'] = "smtp.exmail.qq.com"
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USERNAME'] = 'chenshunkang@lingxun.com'
app.config['MAIL_PASSWORD'] = "Samuelchen0204"
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER']= "chenshunkang@lingxun.com"
mail = Mail(app)

APPID = "wxe1fcbddf1dd93495"
APPSECRET = "5d714168651bcc7e4cf873f8f09c2539"

logger.add("std_out.log")

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.ERROR)


def get_date():
    tsp = time.time()
    timeArray = time.localtime(tsp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


@app.route("/", methods=["GET"])
def index():
    return render_template("api.html")


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),  # 对于当前文件所在路径,比如这里是static下的favicon.ico
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/processCode", methods=["GET"])
def process_code():
    code = request.args.get("code")
    logger.info(f"收到登录请求:code:{code}")
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={APPSECRET}&js_code={code}&grant_type=authorization_code"
    openid = requests.get(url).json()["openid"]
    logger.info(f"获取用户openid成功:openid:{openid}")
    user = models.User.query.get(openid)
    if not user:
        logger.info(f"新用户:openid:{openid}，新建用户档案")
        user = models.User(openid=openid, register=get_date(), latest=get_date(), count=1)
    else:
        logger.info(f"老用户:openid:{openid}，更新用户档案")
        user.count += 1
        user.latest = get_date()
    db.session.add(user)
    db.session.commit()
    logger.info(f"用户:openid:{openid}登录行为结束")
    return {"openid": openid}


@app.route("/questionaire", methods=["GET"])
def get_questionaire():
    # logger.info("收到获取问卷请求")
    questionaire_id = 2
    with open(f"questionaires/{questionaire_id}.json", "r", encoding="utf8") as f:
        data = json.loads(f.read())
    data["form"] = dict()
    for element in data["quiz"]:
        if element["must"] != 1:
            data["form"][element["id"]] = "None"
        else:
            data["form"][element["id"]] = ""
    return data


def upload_sql(openid, form):
    with app.app_context():
        try:
            __temp = ""
            for key in form:
                if key != "openid":
                    __temp += str(f"{key}: {form.get(key)}；")
                questionaire = models.Questionaire(openid=openid, data=__temp)
            db.session.add(questionaire)
            db.session.commit()
            logger.info(f"用户:openid:{openid}问卷数据已上传至数据库")
        except:
            logger.error(f"用户:openid:{openid}数据库上传失败")


def send_mail(openid, form):
    with app.app_context():
        try:
            __temp = ""
            for key in form:
                if key != "openid":
                    __temp += str(f"{key}: {form.get(key)}\n")
            with open("mail.txt", "r") as f:
                recipients = json.loads(f.read())
            message = Message(subject=f'收到新的问卷结果【{form.get("微信号")}-{form.get("英文名")}】【{get_date()}】',
                              recipients=recipients, body=__temp)
            mail.send(message)
            logger.info(f"用户:openid:{openid}问卷数据已发送至邮箱库")
        except:
            logger.error(f"用户:openid:{openid}邮件发送失败")


def save_local(openid, form):
    with app.app_context():
        try:
            __temp = ""
            for key in form:
                if key != "openid":
                    __temp += str(f"{key}: {form.get(key)}\n")
            with open(f"saves/{form.get('微信号')}_{form.get('英文名')}_{str(int(time.time() * 1000))}.log",
                      "w") as f:
                f.write(__temp)
            logger.info(f"用户:openid:{openid}问卷数据已保存至本地文件")
        except:
            logger.error(f"用户:openid:{openid}本地存储失败")


@app.route("/upload", methods=["POST"])
def get_upload_question():
    openid = request.form.get("openid")
    logger.info(f"用户:openid:{openid}提交了问卷结果")
    with open("blacklist.txt", "r") as f:
        blacklist = json.loads(f.read())
    thread_list = list()
    if openid not in blacklist:
        if configs.SAVE_SQL:
            thread_list.append(threading.Thread(target=upload_sql, args=(openid, request.form)))
        if configs.MAIL:
            thread_list.append(threading.Thread(target=send_mail, args=(openid, request.form)))
        if configs.LOCAL:
            thread_list.append(threading.Thread(target=save_local, args=(openid, request.form)))
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
    return "yes"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9520, debug=False)
