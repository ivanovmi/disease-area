from flask_wtf import Form
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import InputRequired


class LoginForm(Form):
    username = StringField('Имя пользователя', [InputRequired()])
    password = PasswordField('Пароль', [InputRequired()])
    login = SubmitField('Войти')
