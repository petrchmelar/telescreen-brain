from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
import os
import shutil
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
# categories_files = db.Table(
#     'categories_files',
#     db.Column('file_id', db.Integer(), db.ForeignKey('file.id')),
#     db.Column('category_id', db.Integer(), db.ForeignKey('category.id')),
# )
#
# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
#     def __str__(self):
#         return self.name
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True, )
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     active = db.Column(db.Boolean())
#     confirmed_at = db.Column(db.DateTime())
#     roles = db.relationship('Role', secondary=roles_users,
#                             backref=db.backref('users', lazy='dynamic'))
#     def __str__(self):
#         return self.email


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __str__(self):
        return self.name


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # defined_name = db.Column(db.String(255), nullable=False)
    # expiration_date = db.Column(db.DateTime, nullable=False)
    # category_id = db.Column(db.Integer(), db.ForeignKey(Category.id), nullable=True)
    # category = db.relationship(Category, backref='File')
    # user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    # user = db.relationship(User)

    def __str__(self):
        return self.name

@db.event.listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.name:
        try:
            pass
            # os.remove(op.join(file_path, target.name))
            # shutil.rmtree(op.join(file_path, os.path.splitext(target.name)[0]))
        except OSError:
            pass

@db.event.listens_for(File, 'after_insert')
def insert_file(mapper, connection, target):
    if target.name:
        try:
            pass
            # os.makedirs(op.join(file_path, os.path.splitext(target.name)[0]))
            # shutil.move(op.join(file_path, target.name), op.join(file_path, target.name))
            # with Image(filename=op.join(file_path, target.name), resolution=200) as img:
            #     img.save(filename=op.join(file_path,  os.path.splitext(target.name)[0],
            #                               '{}.jpg'.format(os.path.splitext(target.name)[0])))
        except OSError:
            pass