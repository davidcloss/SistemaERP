from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ERP.models import Usuarios
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome Usuário:', validators=[DataRequired(), Length(5, 100)])
    senha = PasswordField('Senha:', validators=[DataRequired(), Length(8, 100)])
    confirmacao_senha = PasswordField('Confirme sua senha:', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criar_conta = SubmitField('Criar conta')

    def validate_username(self, username):
        usuario = Usuarios.query.filter_by(username=username.data).first()
        if usuario:
            raise ValidationError('Usuário já cadastrado.')