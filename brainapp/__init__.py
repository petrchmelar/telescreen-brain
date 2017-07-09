from flask import Flask, render_template
from flask_migrate import Migrate
from brainapp.models import *
from brainapp.views import *
from flask_security import SQLAlchemyUserDatastore, Security, login_required
from flask_admin import Admin, helpers as admin_helpers

# flask app setup
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# init db with app
db.init_app(app)
migrate = Migrate(app, db)

# flask security setup
user_data_store = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_data_store)

# flask admin setup
admin = Admin(app)
admin.add_view(FileModelView(File, db.session, u'My Files'))
admin.add_view(FileModelViewAll(File, db.session, u'All Files',endpoint="duplicate_view"))
admin.add_view(UserModelViewAll(Category, db.session, u'Categories'))
admin.add_view(SuperUserModelView(User, db.session, u'Users'))

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


# views
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )