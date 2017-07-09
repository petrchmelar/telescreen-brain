from flask import Flask
from flask_migrate import Migrate
from brainapp.models import db, User, Role
from flask_security import SQLAlchemyUserDatastore, Security

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# init db with app
db.init_app(app)
migrate = Migrate(app, db)

# flask security setup
user_data_store = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_data_store)

# CLI commands
@app.cli.command()
def usersinit():
    user_data_store.find_or_create_role(name='superuser', description='Administrator')
    user_data_store.find_or_create_role(name='user', description='End user')

    if not user_data_store.get_user('admin@admin.com'):
        user_data_store.create_user(email='admin@admin.com', password='admin')
    if not user_data_store.get_user('admin@example.com'):
        user_data_store.create_user(email='user@user.com', password='user')
    db.session.commit()

    user_data_store.add_role_to_user('admin@admin.com', 'superuser')
    user_data_store.add_role_to_user('user@user.com', 'user')
    db.session.commit()

@app.cli.command()
def dbclear():
    db.drop_all()
    db.session.commit()

@app.cli.command()
def dbinit():
    db.create_all()
    db.session.commit()