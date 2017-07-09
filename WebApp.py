import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers, form

from sqlalchemy import event
import os
import os.path as op
import threading, time

import shutil

from wand.image import Image
import datetime


#create file directory
file_path = op.join(op.dirname(__file__), 'files')

try:
    os.mkdir(file_path)
except OSError:
    pass

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

categories_files = db.Table(
    'categories_files',
    db.Column('file_id', db.Integer(), db.ForeignKey('file.id')),
    db.Column('category_id', db.Integer(), db.ForeignKey('category.id')),
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, )
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    def __str__(self):
        return self.email


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __str__(self):
        return self.name


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    defined_name = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    category_id = db.Column(db.Integer(), db.ForeignKey(Category.id), nullable=True)
    category = db.relationship(Category, backref='File')
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User)

    def __str__(self):
        return self.name

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@event.listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.name:
        try:
            os.remove(op.join(file_path, target.name))
            shutil.rmtree(op.join(file_path, os.path.splitext(target.name)[0]))
        except OSError:
            pass

@event.listens_for(File, 'after_insert')
def insert_file(mapper, connection, target):
    if target.name:
        try:
            os.makedirs(op.join(file_path, os.path.splitext(target.name)[0]))
            shutil.move(op.join(file_path, target.name), op.join(file_path, target.name))
            with Image(filename=op.join(file_path, target.name), resolution=200) as img:
                img.save(filename=op.join(file_path,  os.path.splitext(target.name)[0],
                                          '{}.jpg'.format(os.path.splitext(target.name)[0])))
        except OSError:
            pass

# Create customized model view class
class SuperUserModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class UserModelViewAll(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser') or current_user.has_role('user'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
        if not current_user.has_role('superuser'):
            UserModelViewAll.can_delete = False
            UserModelViewAll.can_edit = False
            UserModelViewAll.can_create = True


class UserModelView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser') or current_user.has_role('user'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
        UserModelViewAll.can_delete = True
        UserModelViewAll.can_edit = True
        UserModelViewAll.can_create = True
    def get_query(self):
        return self.session.query(self.model).filter(self.model.user == current_user)

    def get_count_query(self):
        return self.session.query(sqla.view.func.count('*')).filter(self.model.user == current_user)


class FileModelView(UserModelView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.user = current_user
    column_filters = ('name', 'expiration_date', 'category', 'user.email')
    form_create_rules = ('name', 'defined_name', 'expiration_date', 'category')
    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'name': form.FileUploadField,
        'user': current_user
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'name': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False,
            'allowed_extensions': set(['pdf'])
        }
    }

class FileModelViewAll(UserModelViewAll):
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.user = current_user

    form_create_rules = ('name', 'defined_name', 'expiration_date', 'category')
    form_edit_rules = ('defined_name', 'expiration_date', 'category')
    column_filters = ('name', 'expiration_date', 'category')

    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'name': form.FileUploadField,
        'user': current_user
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'name': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False,
            'allowed_extensions': set(['pdf'])
        }
    }


# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# Create admin
admin = flask_admin.Admin(
    app,
    'Digital Signage Service',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Add model views
#admin.add_view(MyModelView(Role, db.session))
admin.add_view(FileModelView(File, db.session, u'My Files'))
admin.add_view(FileModelViewAll(File, db.session, u'All Files',endpoint="duplicate_view"))
admin.add_view(UserModelViewAll(Category, db.session, u'Categories'))
admin.add_view(SuperUserModelView(User, db.session, u'Users'))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )
        db.session.commit()
    return

def expiration_check():
    for file_instance in File.query:
        if(file_instance.expiration_date < datetime.datetime.now()):
            db.session.delete(file_instance)
            db.session.commit()

    threading.Timer(3600, expiration_check).start()
    pass

if __name__ == '__main__':

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    # Create two threads as follows
    app.debug = False
    expiration_check()
    app.run(debug=True, host= '0.0.0.0')
