from flask_script import Manager, Server
from web_listener_9520 import app
from flask_migrate import Migrate, MigrateCommand
from api.exts import db
from api import models

manager = Manager(app)
Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand) # 创建数据库映射命令
manager.add_command('start', Server(port=8000, use_debugger=True)) # 创建启动命令

if __name__ == '__main__':
    manager.run()