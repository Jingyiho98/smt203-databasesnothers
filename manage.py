from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host='127.0.0.1', port=5000))

if __name__ == '__main__':
	manager.run()