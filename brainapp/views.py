from flask_security import current_user
from flask import url_for, redirect, request, abort

from flask_admin.contrib.sqla import ModelView
from flask_admin import form
from flask_admin.contrib import sqla

# Create customized model view class
class SuperUserModelView(ModelView):

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

class UserModelViewAll(ModelView):
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


class UserModelView(ModelView):
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
            # 'base_path': file_path,
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
            # 'base_path': file_path,
            'allow_overwrite': False,
            'allowed_extensions': set(['pdf'])
        }
    }